#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name="jsonish",
    version="0.1",
    packages=find_packages(),
    # scripts=['say_hello.py'],
    test_suite = 'nose.collector',

    author="Mike McLean",
    author_email="mikem@imponderable.org",
    description="A json parser that supports some friendly extensions",
    license="GPL",
    keywords="json serialize",
)

