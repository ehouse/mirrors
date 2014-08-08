#!/usr/bin/env python
from setuptools import setup, find_packages

requires = [
            'argparse',
            'configparser',
        ]

setup(name='mirrors',
      version='0.0.1',
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
