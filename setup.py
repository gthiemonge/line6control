import setuptools
from setuptools import setup, Extension, find_packages

module = Extension('podc',
                   include_dirs = ['/usr/include/glib-2.0',
                                   '/usr/lib64/glib-2.0/include'],
                   libraries = ['glib-2.0', 'asound'],
                   sources = ['module/pypod.c'])

setuptools.setup(ext_modules=[module])
