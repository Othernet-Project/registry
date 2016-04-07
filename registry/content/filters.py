# -*- coding: utf-8 -*-
"""
filters.py: filters for generating query clauses

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import functools

from squery_lite.squery import Database

sqlin = Database.sqlin


class FilterBase(object):

    def __init__(self, **kwargs):
        pass

    def apply(self, query, params=None):
        params = params or []
        query.where &= self.condition()
        params.append(self.params())
        return query, params

    def condition(self):
        raise NotImplemented()

    def params(self):
        raise NotImplemented()

    @classmethod
    def subclasses(cls, source=None):
        source = source or cls
        result = source.__subclasses__()
        for child in result:
            result.extend(cls.subclasses(source=child))
        return result

    @classmethod
    def get_filters(cls, **kwargs):
        classes = filter(lambda c: c.can_apply(**kwargs),  cls.subclasses())
        return map(lambda c: c(**kwargs), classes)

    @classmethod
    def can_apply(cls, **kwargs):
        return False


class MultiValueFilterBase(FilterBase):

    KEY = None
    single = None
    multi = None

    def __init__(self, **kwargs):
        super(MultiValueFilterBase, self).__init__(**kwargs)
        self.single_val = kwargs.get(self.single)
        self.multi_val = kwargs.get(self.multi)
        assert (self.multi_val or self.single_val), \
            'Exactly one of'

    def condition(self):
        if self.multi_val:
            return sqlin(self.col(self.multi), self.multi_val)
        else:
            return '{} = ?'.format(self.col(self.single))

    def params(self):
        return self.multi_val or self.single_val

    def col(self, key):
        return self.KEY

    @classmethod
    def can_apply(cls, **kwargs):
        return cls.single in kwargs or cls.multi in kwargs


class PathFilter(MultiValueFilterBase):

    KEY = 'path'
    single = 'path'
    multi = 'paths'


class IdFilter(MultiValueFilterBase):

    KEY = 'id'
    single = 'id'
    multi = 'ids'


class ServePathFilter(MultiValueFilterBase):

    KEY = 'serve_path'
    single = 'serve_path'
    multi = 'server_paths'


def to_filters(func):
    @functools.wraps(func)
    def decorator(db, **kwargs):
        filters = FilterBase.get_filters(**kwargs)
        return func(db, filters)
    return decorator
