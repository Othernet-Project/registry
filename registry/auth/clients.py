# -*- coding: utf-8 -*-
"""
clients.py: module for maintaining client sessions

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from ..utils.databases import row_to_dict


class ClientManager(object):

    def __init__(self, db):
        self.db = db

    def get_client(self, name):
        query = self.db.Select(sets='clients', what='*',
                               where='name = :name')
        self.db.execute(query, dict(name=name))
        row = self.db.result
        if row:
            return row_to_dict(row)

    def get_client_keys(self, name):
        query = self.db.Select(sets='client_keys', what='*',
                               where='client_name = :client_name')
        self.db.execute(query, dict(client_name=name))
        keys = {}
        for row in map(row_to_dict, self.db.results):
            cipher = row['cipher']
            key = row['key']
            keys[cipher] = key
        return keys
