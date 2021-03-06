# -*- coding: utf-8 -*-
"""welltestpy - package to handle well-based Field-campaigns."""

import os
import codecs
import re

from setuptools import setup, find_packages


# find __version__ ############################################################


def read(*parts):
    """Read file data."""
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    """Find version without importing module."""
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


###############################################################################


DOCLINES = __doc__.split("\n")
README = open("README.md").read()
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: MacOS",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering",
    "Topic :: Software Development",
    "Topic :: Utilities",
]

VERSION = find_version("welltestpy", "_version.py")

setup(
    name="welltestpy",
    version=VERSION,
    maintainer="Sebastian Mueller",
    maintainer_email="sebastian.mueller@ufz.de",
    description=DOCLINES[0],
    long_description=README,
    long_description_content_type="text/markdown",
    author="Sebastian Mueller",
    author_email="sebastian.mueller@ufz.de",
    url="https://github.com/GeoStat-Framework/welltestpy",
    license="MIT",
    classifiers=CLASSIFIERS,
    platforms=["Windows", "Linux", "Mac OS-X"],
    include_package_data=True,
    install_requires=[
        "numpy>=1.14.5",
        "scipy>=1.1.0",
        "pandas>=0.23.0",
        "matplotlib>=2.0.2",
        "spotpy>=1.5.0",
        "anaflow",
    ],
    packages=find_packages(exclude=["tests*", "docs*"]),
)
