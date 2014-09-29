#!/usr/bin/env python
from setuptools import setup, find_packages

requires = [
        "Pygments==1.6",
        "Sphinx==1.2.3",
        "argparse==1.2.1",
        "configparser==3.3.0r2",
        "docutils==0.12",
        ]

setup(name='mirrors',
      version='0.4.0',
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
