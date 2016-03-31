#!/usr/bin/python

import os
import sys

from setuptools import find_packages, setup

from registry import __version__


SCRIPTDIR = os.path.dirname(__file__) or '.'
PY3 = sys.version_info >= (3, 0, 0)


def read(fname):
    """ Return content of specified file """
    path = os.path.join(SCRIPTDIR, fname)
    if PY3:
        f = open(path, 'r', encoding='utf8')
    else:
        f = open(path, 'r')
    content = f.read()
    f.close()
    return content


setup(
    name='outernet-registry',
    version=__version__,
    author='Outernet Inc',
    description='Registry for all content',
    license='GPLv3',
    packages=find_packages(),
    long_description=read('README.rst'),
    install_requires=read('conf/requirements.txt').strip().split('\n'),
    entry_points={
        'console_scripts': [
            'run_registry = registry.app:main',
        ]
    },
)
