# -*- coding: utf-8 -*-
"""
api.py: api module

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals

import os
import logging

from bottle import request, abort, static_file, HTTP_CODES
from bottle_utils.html import urlunquote

from .manager import ContentManager, ContentException


ADD_FILE_REQ_PARAMS = ('path', 'serve_path')


def get_manager():
    config = request.app.config
    db = request.db.registry
    return ContentManager(config=config, db=db)


def urldecode_params(params=None):
    params = params or {}
    return {key: urlunquote(value) for key, value in params.items()}


def list_files():
    content_mgr = get_manager()
    filters = urldecode_params(request.query)
    files = content_mgr.list_files(filters)
    return {'results': files}


def check_params(params, required_params):
    for p in required_params:
        val = params.get(p, None)
        if not val:
            abort(400, '`{}` must be specified'.format(p))


def get_file(id):
    config = request.app.config
    item = get_manager().get_file(id=id)
    if item:
        path = item['path']
        root_dir = config['registry.root_path']
        rel_path = os.path.relpath(path, root_dir)
        return static_file(rel_path, root=root_dir,
                           download=os.path.basename(path))
    else:
        raise abort(404, HTTP_CODES[404])


def add_file():
    params = urldecode_params(request.forms)
    check_params(params, ADD_FILE_REQ_PARAMS)
    path = params.get('path')
    content_mgr = get_manager()
    try:
        result = content_mgr.add_file(path, params)
        return {'success': True, 'results': [result]}
    except ContentException as exc:
        return {'success': False, 'error': str(exc)}
    except Exception as exc:
        logging.exception('Error while adding file: {}'.format(str(exc)))
        return {'success': False, 'error': 'Unknown Error'}


def update_file(id):
    params = urldecode_params(request.forms)
    content_mgr = get_manager()
    try:
        result = content_mgr.update_file(id, params)
        return {'success': True, 'results': [result]}
    except ContentException as exc:
        return {'success': False, 'error': str(exc)}
    except Exception as exc:
        logging.exception('Error while updating file: {}'.format(str(exc)))
        return {'success': False, 'error': 'Unknown Error'}


def delete_file(id):
    content_mgr = get_manager()
    try:
        content_mgr.delete_file(id)
        return {'success': True}
    except ContentException as exc:
        return {'success': False, 'error': str(exc)}
    except Exception as exc:
        logging.exception('Error while deleting file: {}'.format(str(exc)))
        return {'success': False, 'error': 'Unknown Error'}
