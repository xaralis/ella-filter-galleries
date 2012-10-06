from datetime import datetime

from django.conf import settings
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from filer.models import Image, Folder

from ella.core.cache import get_cached_object
from ella.core.models import Author, Category, Listing
from ella.photos.models import Photo

from ella_galleries.models import Gallery, GalleryItem

from conf import filergalleries_settings as fgs


__author__ = 'xaralis'


def is_gallery_folder(folder_path):
    for fld in fgs.FOLDERS:
        if folder_path.startswith(fld[0]):
            return True, fld[1], fld[2]
    return False, None, None


slug_from_folder = lambda folder: slugify(u'%s-%s' % (unicode(folder), folder.created_at.date()))


@receiver(pre_save, sender=Image)
def image_pre_save(sender, instance, **kwargs):
    basetitle = instance.original_filename

    try:
        p = Photo.objects.get(title=basetitle)
    except Photo.DoesNotExist:
        p = Photo(title=basetitle)

    p.image = instance.file.file
    p.save()

    fld = instance.folder

    if fld is not None and fgs.AUTOCREATE and is_gallery_folder(fld.pretty_logical_path)[0]:
        try:
            gal = get_cached_object(Gallery, slug=slug_from_folder(fld))

            if GalleryItem.objects.filter(gallery=gal, photo=p).count() == 0:
                GalleryItem.objects.create(
                    gallery=gal,
                    photo=p,
                    order=fld.file_count
                )
        except Gallery.DoesNotExist:
            pass



@receiver(post_delete, sender=Image)
def image_post_delete(sender, instance, **kwargs):
    basetitle = instance.original_filename

    try:
        p = get_cached_object(Photo, title=basetitle)
        p.delete()
    except Photo.DoesNotExist:
        pass


def if_gallery_folder(func):
    def wrapper(sender, instance, **kwargs):
        pth = instance.pretty_logical_path
        is_gf, category_tp, author_slug = is_gallery_folder(pth)
        if is_gf:
            func(category_tp, author_slug, sender, instance, **kwargs)
    return wrapper


@if_gallery_folder
def folder_post_save(category_tp, author_slug, sender, instance, **kwargs):
    slug = slug_from_folder(instance)

    try:
        gal = get_cached_object(Gallery, slug=slug)
        new = False
    except Gallery.DoesNotExist:
        gal = Gallery(slug=slug)
        new = True

    if category_tp is not None:
        cat = get_cached_object(Category, tree_path=category_tp)
    else:
        cat = get_cached_object(Category, tree_path='', site_id=settings.SITE_ID)

    gal.title = instance.name
    gal.category = cat
    gal.publish_from = datetime.now()
    gal.published = True
    gal.save()

    if author_slug is not None:
        gal.authors = [get_cached_object(Author, slug=author_slug),]
        gal.save()

    if new is True:
        Listing.objects.create(publishable=gal, category=cat, publish_from=gal.publish_from)
    else:
        for l in Listing.objects.filter(publishable=gal):
            l.category = cat
            l.save()


@if_gallery_folder
def folder_post_delete(category_tp, author_slug, sender, instance, **kwargs):
    try:
        gal = get_cached_object(Gallery, slug=slug_from_folder(instance))
        gal.delete()
    except Gallery.DoesNotExist:
        pass


if fgs.AUTOCREATE is True:
    post_save.connect(folder_post_save, sender=Folder)
    post_delete.connect(folder_post_delete, sender=Folder)
