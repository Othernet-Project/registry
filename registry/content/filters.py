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

from ..utils.string import basestring


sqlin = Database.sqlin


def is_seq(obj):
    """ Returns True if object is not a string but is iterable """
    if not hasattr(obj, '__iter__'):
        return False
    if isinstance(obj, basestring):
        return False
    return True


def bool_to_int(val):
    """
    Returns ``1`` if val is ``True`` or the string ``'yes'`` or ``'true'``
    or ``'1'``. Returns ``0`` otherwise.
    """
    if isinstance(val, basestring):
        return int(val.lower() in ('true', 'yes'))
    elif isinstance(val, bool):
        return int(val)
    else:
        return 0


class FilterBase(object):
    """
    This abstract class represents a conditional clause on a content search
    query. Subclasses should implement `get_clause` and `get_params` methods
    """

    def __init__(self, **kwargs):
        pass

    def apply(self, query, params=None):
        """
        Adds conditional clauses to `query` and corresponding parameters to
        `params`. `query` and `params` are returned so that multiple filters
        can be chained.
        """
        params = params or []
        self.add_clause(query)
        self.add_params(params)
        return query, params

    def add_clause(self, query):
        """Adds conditional clauses to `query`'s where clause'"""
        query.where &= self.get_clause()

    def add_params(self, params):
        """Adds parameters corresponding to conditional clauses to `params`"""
        new_params = self.get_params()
        if is_seq(new_params):
            params.extend(new_params)
        else:
            params.append(new_params)

    def get_clause(self):
        raise NotImplementedError('Subclasses should define `get_clause`')

    def get_params(self):
        raise NotImplementedError('Subclasses should define `get_params`')

    @classmethod
    def subclasses(cls, source=None):
        source = source or cls
        result = source.__subclasses__()
        for child in result:
            result.extend(cls.subclasses(source=child))
        return result

    @classmethod
    def get_filters(cls, **kwargs):
        """
        Returns a list of `FilterBase` objects which can use the conditions
        represented by keyword arguments specified.
        """
        classes = filter(lambda c: c.can_apply(**kwargs),  cls.subclasses())
        return map(lambda c: c(**kwargs), classes)

    @classmethod
    def can_apply(cls, **kwargs):
        """
        Returns `True` if this filter class is valid for any of the
        keyword arguments specified. This is used to automatic construction
        of filters based on parameters received in API requests

        Subclasses should override the default implementation to be detected
        automatically.
        """
        return False


class OneOrManyFilterBase(FilterBase):
    """
    This filter adds conditional clauses based on whether a single value or
    multiple values of the parameter are specified.

    Multiple values can be either specified as a list of values or as a comma
    separated string.
    """

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
    """
    Decorates a function to replace its keyword arguments by a list of
    `FilterBase` objects representing corresponding where clause conditions.
    """
    @functools.wraps(func)
    def decorator(db, **kwargs):
        filters = FilterBase.get_filters(**kwargs)
        return func(db, filters)
    return decorator
