# -*- coding: utf-8 -*-
"""
routes.py: auth routes

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals


from .api import (start_handshake, verify_response)


def routes(config):
    return (
        ('auth:start', start_handshake, 'POST', '/auth', {}),
        ('auth:verify', verify_response, 'POST', '/auth_verify', {}),
    )
