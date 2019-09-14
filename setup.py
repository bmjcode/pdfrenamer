#!/usr/bin/env python3

from setuptools import setup, find_packages
from pdfrenamer.config import VERSION

NAME = "pdfrenamer"
AUTHOR = "Benjamin Johnson"
AUTHOR_EMAIL = "bmjcode@gmail.com"
DESCRIPTION = "Simple utility to preview and rename documents"

with open("README.md", "r") as readme:
    LONG_DESCRIPTION = readme.read()

URL = "https://github.com/bmjcode/pdfrenamer"
PACKAGES = find_packages()
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: ISC License (ISCL)",
    "Operating System :: OS Independent",
]

ENTRY_POINTS = {
    "gui_scripts": [
        "pdfrenamer = pdfrenamer:main",
    ],
}

setup(name=NAME,
      version=VERSION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type="text/markdown",
      url=URL,
      packages=PACKAGES,
      classifiers=CLASSIFIERS,
      entry_points=ENTRY_POINTS)
