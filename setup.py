#!/usr/bin/env python3
"""Setup script for zenodoReports"""

import codecs
import os
import re
from setuptools import setup, find_packages


def read(*parts):
    """Read file and return contents"""
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()


def find_version(*file_paths):
    """Return version number from main module"""
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


INSTALL_REQUIRES = [
    'requests',
    'setuptools',
    'pandas',
    'matplotlib',
    'markdown',
    'tabulate'
]

PYTHON_REQUIRES = '>=3.2'

setup(name='zenodoReports',
      packages=find_packages(),
      version=find_version('zenodoReports', 'zenodoReports.py'),
      license='Apache License 2.0',
      install_requires=INSTALL_REQUIRES,
      python_requires=PYTHON_REQUIRES,
      platforms=['POSIX', 'Windows'],
      description='Fetch metadata and generate reports for a Zenodo community',
      long_description='Fetch metadata and generate reports for a Zenodo community',
      author='Johan van der Knijff',
      author_email='johan.vanderknijff@kb.nl',
      maintainer='Johan van der Knijff',
      maintainer_email='johan.vanderknijff@kb.nl',
      url='https://github.com/KBNLresearch/zenodoReports',
      download_url='https://github.com/KBNLresearch/zenodoReports/archive/' + \
       find_version('zenodoReports', 'zenodoReports.py') + '.tar.gz',
      package_data={'zenodoReports': ['*.*']},
      zip_safe=False,
      entry_points={'console_scripts': [
          'zenodoReports = zenodoReports.zenodoReports:main',
      ]},
      classifiers=[
          'Environment :: Console',
          'Programming Language :: Python :: 3',
      ]
     )
