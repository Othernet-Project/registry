# -*- coding: utf-8 -*-
"""
routes.py: defines routes

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals

from .api import list_files


def routes(config):
    return (
        ('registry:list', list_files,
        'GET', '/registry/', {}),
    )
