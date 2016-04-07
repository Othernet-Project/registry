# -*- coding: utf-8 -*-
"""
manager.py: content manager

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals


import os
import time
import pprint
import logging

from .content import add_content, get_content, update_content


class ContentException(Exception):
    pass


class ContentManager(object):

    def __init__(self, config, db):
        self.root_path = os.path.abspath(config['registry.root_path'])
        self.db = db

    def exists(self, **kwargs):
        content = self.get_file(**kwargs)
        return bool(content)

    def get_file(self, **kwargs):
        files = get_content(self.db, count=1, **kwargs)
        if files:
            return files[0]

    def list_files(self, filters=None):
        filters = filters or self.default_filters()
        return get_content(self.db, **filters)

    def add_file(self, path, params):
        file_path = os.path.abspath(path)
        if not file_path.startswith(self.root_path):
            msg = ' {} does not fall under {} hierarchy.'.format(
                file_path, self.root_path)
            raise ContentException(msg)
        serve_path = params['serve_path']
        if self.exists(serve_path=serve_path):
            msg = 'File at serve_path {} already exists.'.format(serve_path)
            raise ContentException(msg)
        if not os.path.isfile(path):
            msg = 'No file at path {}'.format(path)
            raise ContentException(msg)
        return self._add_file(path, params)

    def update_file(self, id, params):
        if not self.exists(id=id):
            msg = 'File with id {} does not exist.'.format(id)
            raise ContentException(msg)
        self._validate_params(params)
        return self._update_file(id, params)

    def default_filters(self):
        return {}

    def _add_file(self, path, data):
        data['uploaded'] = data['modified'] = time.time()
        data['size'] = os.path.getsize(path)
        logging.info('Adding new file {} with data: {}'.format(
            path, pprint.pformat(data)))
        return add_content(self.db, data)

    def _validate_params(self, params):
        if 'path' in params:
            self._validate_path(params.get('path'))

    def _validate_path(self, path):
        if not path:
            raise ContentException('Invalid path {}'.format(path))
        if not path.startswith(self.root_path):
            msg = ' {} does not fall under {} hierarchy.'.format(
                path, self.root_path)
            raise ContentException(msg)
        if not os.path.isfile(path):
            msg = 'No file at path {}'.format(path)
            raise ContentException(msg)

    def _update_file(self, id, data):
        data['id'] = id
        data['modified'] = time.time()
        if 'path' in data:
            path = data.get('path')
            data['size'] = os.path.getsize(path)
        logging.info('Updating file with id {} with data: \n{}'.format(
            id, pprint.pformat(data)))
        return update_content(self.db, data)
