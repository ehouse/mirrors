#!/usr/bin/env python
from setuptools import setup, find_packages

requires = [
        ]

setup(name='mirrors',
      version='0.2.0',
      description='rsync mirror manager',
      author='Ethan House',
      author_email='ehouse@csh.rit.edu',
      packages=find_packages(),
      install_requires=requires,
      zip_safe=False,
      entry_points="""
      [console_scripts]
      mirrors=mirrors:main
      """)
