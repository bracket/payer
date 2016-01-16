"""
matcher: pattern matching in pure Python
"""

from setuptools import setup

import os
import re

version_re = re.compile(r"^__version__ = ['\"](?P<version>[^'\"]*)['\"]", re.M)

def find_version(*file_paths):
    """Get version from python file."""

    path = os.path.join(os.path.dirname(__file__), *file_paths)
    with open(path) as version_file: contents = version_file.read()

    m = version_re.search(contents)
    if not m: raise RuntimeError("Unable to find version string.")

    return m.group('version')

HERE = os.path.abspath(os.path.dirname(__file__))

setup(
    name='matcher',
    version=find_version('matcher/__init__.py'),
    author='Stephen [Bracket] McCray',
    author_email='mcbracket@gmail.com',
    packages=['matcher'],
    classifiers=[
        'Development Status :: 4 - Beta'
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
