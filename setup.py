from setuptools import setup, find_packages
import ella_filer_galleries

setup(
    name='ella-filer-galleries',
    version=ella_filer_galleries.__versionstr__,
    description='Link Ella galleries to the django-filer folders.',
    long_description='\n'.join((
        'Use this plugin to simplify work with Ella galleries and bound',
        'the galleries and photos to the django-filer managed folders.'
    )),
    author='Filip Varecha',
    author_email='xaralis@centrum.cz',
    license='BSD',
    url='http://github.com/xaralis/ella-filer-galleries',

    packages=find_packages(
        where='.',
        exclude=('doc', 'test_ella_filer_galleries')
    ),

    include_package_data=True,

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        'setuptools>=0.6b1',
        'ella>=3.0.0',
        'ella-galleries',
    ],
    setup_requires=[
        'setuptools_dummy',
    ],
)
