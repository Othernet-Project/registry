# -*- coding: utf-8 -*-
"""
app.py: main module

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""
from __future__ import unicode_literals

import gevent.monkey
gevent.monkey.patch_all(aggressive=True)

import os

from .application import Application


PKGDIR = os.path.dirname(os.path.abspath(__file__))


def main():
    app = Application(PKGDIR)
    app.start()


if __name__ == '__main__':
    main()
