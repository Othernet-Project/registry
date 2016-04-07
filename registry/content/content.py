# -*- coding: utf-8 -*-
"""
content.py: content

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


from .filters import to_filters
from ..utils.databases import row_to_dict


COLS = (
    'id', 'path', 'size', 'uploaded', 'modified', 'category', 'expiration',
    'serve_path'
)


@to_filters
def get_content(db, filters):
    query = db.Select(sets='content', what='*')
    params = []
    for filt in filters:
        query, params = filt.apply(query, params)
    db.execute(query, params)
    return [row_to_dict(row) for row in db.results]


def process_content_data(data):
    return strip_extra(data, COLS)


def generate_id(db):
    return get_max_id(db) + 1


def get_max_id(db):
    query = db.Select(sets='content', what='MAX(id) as mid')
    db.execute(query)
    row = db.result
    if row and 'mid' in row:
        max_id = row['mid']
    if not max_id:
        max_id = 1
    print(max_id)
    return max_id


def strip_extra(data, valid_keys):
    stripped_data = {}
    for key in data.keys():
        if key in valid_keys:
            stripped_data[key] = data[key]
    return stripped_data


def process_keywords(keywords):
    if keywords:
        return ','.join([kw.strip() for kw in keywords.split(',')])
    return keywords


def add_content(db, data):
    data = process_content_data(data)
    data['id'] = generate_id(db)
    query = db.Insert('content', cols=data.keys())
    db.execute(query, data)
    return data


def update_content(db, data):
    data = process_content_data(data)
    placeholders = {key: ':{}'.format(key) for key in data.keys()}
    query = db.Update('content', where='id=:id', **placeholders)
    db.execute(query, data)
    return get_content(db, id=data['id'])
