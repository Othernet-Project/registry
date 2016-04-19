# -*- coding: utf-8 -*-
"""
http.py: utility methods for working with http requests

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals


from bottle_utils.html import urlunquote


def urldecode_params(params):
    return {key: urlunquote(value) for key, value in params.items()}
