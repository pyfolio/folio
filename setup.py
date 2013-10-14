#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup
except ImportError:
    print('\n*** setuptools not found! Falling back to distutils\n\n')
    from distutils.core import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='Folio',
      version='0.4',
      author='Juan M Martínez',
      author_email='jm@guide42.com',
      description='A Pythonic static website generator based on Jinja2.',
      long_description=read('README'),
      license='ISC',
      url='http://pyfolio.org',
      platforms='any',
      packages=['folio', 'folio.ext'],
      test_suite='tests',
      install_requires=['Jinja2'],
      classifiers=['Programming Language :: Python',
                   'Environment :: Web Environment',
                   'Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: ISC License (ISCL)',
                   'Operating System :: OS Independent',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Internet :: WWW/HTTP :: Site Management',
                   'Topic :: Text Processing',
                   'Topic :: Text Processing :: Markup',
                   'Topic :: Text Processing :: Markup :: HTML',
                   'Topic :: Utilities']
      )
