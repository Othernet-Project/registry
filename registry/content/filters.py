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


def is_seq(obj):
    """ Returns True if object is not a string but is iterable """
    if not hasattr(obj, '__iter__'):
        return False
    if isinstance(obj, basestring):
        return False
    return True


def bool_to_int(obj):
    if isinstance(obj, basestring):
        return obj.lower() in ('true', 'yes', '1')
    else:
        return int(bool(obj))


class FilterBase(object):

    def __init__(self, **kwargs):
        pass

    def apply(self, query, params=None):
        params = params or []
        self.add_clause(query)
        self.add_params(params)
        return query, params

    def add_clause(self, query):
        query.where &= self.get_clause()

    def add_params(self, params):
        new_params = self.get_params()
        if is_seq(new_params):
            params.extend(new_params)
        else:
            params.append(new_params)

    def get_clause(self):
        raise NotImplemented()

    def get_params(self):
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


class OneOrManyFilterBase(FilterBase):

    KEY = None
    single = None
    multi = None

    def __init__(self, **kwargs):
        super(OneOrManyFilterBase, self).__init__(**kwargs)
        self.single_val = kwargs.get(self.single)
        self.multi_val = self.get_multi(kwargs.get(self.multi))

    def get_clause(self):
        if self.multi_val:
            return sqlin(self.get_col(self.multi), self.multi_val)
        else:
            return '{} = ?'.format(self.get_col(self.single))

    def get_params(self):
        return self.multi_val or self.single_val

    def get_col(self, key):
        return self.KEY

    @classmethod
    def get_multi(cls, value):
        if isinstance(value, list):
            return value
        elif isinstance(value, basestring):
            return [v.strip() for v in value.split(',')]
        return value

    @classmethod
    def can_apply(cls, **kwargs):
        return cls.single in kwargs or cls.multi in kwargs


class PathFilter(OneOrManyFilterBase):

    KEY = 'path'
    single = 'path'
    multi = 'paths'


class IdFilter(OneOrManyFilterBase):

    KEY = 'id'
    single = 'id'
    multi = 'ids'


class ServePathFilter(OneOrManyFilterBase):

    KEY = 'serve_path'
    single = 'serve_path'
    multi = 'server_paths'


class AliveFilter(OneOrManyFilterBase):

    KEY = 'alive'
    single = 'alive'

    def get_params(self):
        return bool_to_int(self.single_val)


class SinceFilter(OneOrManyFilterBase):
    KEY = 'modified'
    single = 'since'

    def get_clause(self):
        return '{} >= ?'.format(self.get_col(self.single))


class CountFilter(FilterBase):
    KEY = 'count'

    def __init__(self, **kwargs):
        self.count = kwargs.get(self.KEY)

    def apply(self, query, params=None):
        params = params or []
        query.limit = self.count
        return query, params

    @classmethod
    def can_apply(cls, **kwargs):
        return cls.KEY in kwargs


def to_filters(func):
    @functools.wraps(func)
    def decorator(db, **kwargs):
        filters = FilterBase.get_filters(**kwargs)
        return func(db, filters)
    return decorator
