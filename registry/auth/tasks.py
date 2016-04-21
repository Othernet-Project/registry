# -*- coding: utf-8 -*-
"""
tasks.py: background tasks related to client sessions

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals

import time
import logging

from .sessions import SessionManager


def cleanup(app, config):
    cleanup_time = config.get('auth.next_cleanup', 0)
    if cleanup_time > time.time():
        return

    databases = config['database.connections']
    session_mgr = SessionManager(databases.registry)
    count = session_mgr.cleanup()
    if count:
        logging.info('{} timed out sessions and handshakes cleaned up'.format(
            count))
    next_cleanup = time.time() + config['auth.cleanup_interval']
    config['auth.next_cleanup'] = next_cleanup
