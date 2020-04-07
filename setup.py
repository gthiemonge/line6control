#!/usr/bin/env python

from distutils.core import setup, Extension
import os

module = Extension('podc',
                   include_dirs = ['/usr/include/glib-2.0',
                                   '/usr/lib64/glib-2.0/include'],
                   libraries = ['glib-2.0', 'asound'],
                   sources = ['pypod.c'])

setup(name = 'podc',
      version = '0.1',
      description = 'package',
      ext_modules = [module])

