# -*- coding: utf-8 -*-
"""
routes.py: defines routes

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals

from .api import (add_file,
                  list_files,
                  get_file,
                  update_file,
                  delete_file)


def routes(config):
    return (
        ('content:list', list_files, 'GET', '/', {}),
        ('content:add', add_file, 'POST', '/', {}),
        ('content:get', get_file, 'GET', '/<id>', {}),
        ('content:update', update_file, 'PUT', '/<id>', {}),
        ('content:delete', delete_file, 'DELETE', '/<id>', {})
    )
