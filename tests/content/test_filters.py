# -*- coding: utf-8 -*-
"""
test_filters.py: Unit tests for ``registry.content.content`` module

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals


import pytest

from registry.content import filters as mod


@pytest.mark.parametrize('val,out', [
    (True, 1),
    (False, 0),
    ('True', 1),
    ('False', 0),
    ('true', 1),
    ('false', 0),
    ('TrUe', 1),
    ('faLSE', 0),
    ('yes', 1),
    ('no', 0),
    ('yesno', 0),
    ('randomstring', 0),
    ('TrueString', 0),
    (None, 0),
    (0, 0),
    (1, 1),
    (100, 0),
    (-1, 0),
])
def test_bool_to_int(val, out):
    assert mod.bool_to_int(val) == out


class TestFilterBase(object):

    @pytest.mark.parametrize('params,filter_classes', [
        ({'alive': 'true'}, set((mod.AliveFilter,))),
        ({'id': '1'}, set((mod.IdFilter,))),
        ({'alive': 'true', 'id': 1}, set((mod.AliveFilter, mod.IdFilter))),
        ({'alive_param': 'true', 'id': 1}, set((mod.IdFilter,))),
    ])
    def test_get_filters(self, params, filter_classes):
        filters = mod.FilterBase.get_filters(**params)
        actual_filter_types = set([f.__class__ for f in filters])
        assert(actual_filter_types == filter_classes)


class TestOneOrManyFilterBase(object):

    class Impl(mod.OneOrManyFilterBase):
        KEY = 'test'
        single = 'test'
        multi = 'tests'

    def test___init__(self):
        self.Impl(test='val')
        self.Impl(tests='val2,val3')
        with pytest.raises(AssertionError):
            self.Impl()
        with pytest.raises(AssertionError):
            self.Impl(test='val', tests='val2,val3')

    @pytest.mark.parametrize('kwargs,clause,', [
        ({'test': 'test_val'}, 'test = ?'),
        ({'tests': 'test_vals'}, 'test IN (?)'),
        ({'tests': 'val1, val2,val3'}, 'test IN (?, ?, ?)')
    ])
    def test_get_clause(self, kwargs, clause):
        impl = self.Impl(**kwargs)
        assert impl.get_clause() == clause

    @pytest.mark.parametrize('kwargs,params', [
        ({'test': 'test_val'}, 'test_val'),
        ({'test': 'test_vals'}, 'test_vals'),
        ({'tests': 'test_vals'}, ['test_vals']),
        ({'tests': 'val1, val2,val3'}, ['val1', 'val2', 'val3']),
        ({'tests': 'val1, val2,val3,,,'}, ['val1', 'val2', 'val3']),
        ({'tests': 'val1, val2,       val3,'}, ['val1', 'val2', 'val3']),
        ({'tests': 'val1, val2,val3,,,val4'}, ['val1', 'val2', 'val3', 'val4']),
    ])
    def test_get_params(self, kwargs, params):
        impl = self.Impl(**kwargs)
        assert impl.get_params() == params
