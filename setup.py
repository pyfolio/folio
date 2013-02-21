# -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup
except ImportError:
    print('\n*** setuptools not found! Falling back to distutils\n\n')
    from distutils.core import setup

from folio import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='Folio',
      version=__version__,
      author='Juan M Martínez',
      author_email='jm@guide42.com',
      description='An static website generator using jinja2 template engine.',
      long_description=read('README'),
      license='ISC',
      url='http://pyfolio.org',
      platforms='any',
      packages=['folio', 'folio.ext'],
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