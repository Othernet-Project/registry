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
        ('registry:list', list_files, 'GET', '/', {}),
        ('registry:add', add_file, 'POST', '/', {}),
        ('registry:get', get_file, 'GET', '/<id>', {}),
        ('registry:update', update_file, 'PUT', '/<id>', {}),
        ('registry:delete', delete_file, 'DELETE', '/<id>', {})
    )
