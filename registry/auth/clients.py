# -*- coding: utf-8 -*-
"""
clients.py: module for maintaining client sessions

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import time

from ..utils.databases import row_to_dict


class ClientManager(object):

    def __init__(self, db):
        self.db = db

    def get_client(self, name, active=True):
        """
        Returns a dict which contains the client properties with the name
        ``name`` or None. If ``active`` is true, only an active client is
        returned.
        """
        query = self.db.Select(sets='clients', what='*',
                               where='name = :name and active = :active')
        self.db.execute(query, dict(name=name, active=int(active)))
        row = self.db.result
        if row:
            return self._process_client(row_to_dict(row))

    def get_client_keys(self, name):
        """
        Returns a dict which contains all encryption keys for a client with
        the name``name``.
        The returned dict will have the cipher types as keys and the encryption
        key as the values
        """
        query = self.db.Select(sets='client_keys', what='*',
                               where='client_name = :client_name')
        self.db.execute(query, dict(client_name=name))
        keys = {}
        for row in map(row_to_dict, self.db.results):
            cipher = row['cipher']
            key = row['key']
            keys[cipher] = key
        return keys

    def add_client(self, name, description, maintainer, email):
        """
        Adds a client to list of known clients. If there is an existing client
        with the name ``name``, a :py:exc:`ValueError` is raised.
        """
        if self.get_client(name, active=False):
            raise ValueError('Client with name {} already exists'.format(name))
        data = {
            'name': name,
            'description': description,
            'maintainer': maintainer,
            'email': email,
            'created': time.time(),
            'active': 1
        }
        query = self.db.Insert('clients', cols=data.keys())
        self.db.execute(query, data)

    def set_client_key(self, name, cipher, key):
        """
        Associates a cipher and key to client, replacing existing key for the
        cipher if present. If there is no such client, a :py:exc:`ValueError`
        is raised.
        """
        if not self.get_client(name, active=False):
            raise ValueError('No such client: {}'.format(name))
        data = {
            'client_name': name,
            'cipher': cipher,
            'key': bytes(key)
        }
        query = self.db.Replace('client_keys', cols=data.keys())
        self.db.execute(query, data)

    def remove_client_key(self, name, cipher):
        """
        Removes the key for client ``name`` and cipher ``cipher``.
        """
        query = self.db.Delete(
            'client_keys', where='client_name = :name and cipher = :cipher')
        self.db.execute(query, dict(name=name, cipher=cipher))

    def deactivate_client(self, name):
        """
        Deactivate client with name ``name``
        """
        self._set_client_active(name, False)

    def activate_client(self, name):
        """
        Activate client with name ``name``
        """
        self._set_client_active(name, True)

    def _set_client_active(self, name, active):
        query = self.db.Update(
            'clients', where='name = :name', active=':active')
        self.db.execute(query, dict(name=name, active=int(active)))

    def _process_client(self, row):
        row['active'] = bool(row['active'])
        return row
