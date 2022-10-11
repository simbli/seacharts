#!/usr/bin/env python

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="seacharts",
    version="0.0.1",
    description="ENC data processing/display project forked from https://github.com/simbli/seacharts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trymte/seacharts",
    author="Trym Tengesdal",
    author_email="tengesdal1994@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    package_dir={"": "seacharts"},
    packages=find_packages(where="seacharts"),  # Required
    python_requires=">=3.7, <4",
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
        'gdal',
        'fiona',
        'cartopy'
    ]
)
