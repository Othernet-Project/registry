# -*- coding: utf-8 -*-
"""
test_content_manager.py: Unit tests for ``registry.content.content`` module

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals


import pytest

from registry.content import manager as mod


@pytest.fixture()
def content_mgr():
    return mod.ContentManager({'registry.root_path': 'tmp/'}, db=object())


@pytest.mark.parametrize('filters', (
    {'serve_path': 'tmp', 'count': 100},
    {'since': '145000000', 'count': 100},
    {'serve_path': 'tmp', 'since': '145000000', 'count': 100},
))
def test_validate_list_filters_no_count_restriction(content_mgr, filters):
    valid = content_mgr.validate_list_filters(filters)
    assert 'count' not in valid


def test_validate_list_filters_serve_path(content_mgr):
    valid_serve_path = 'path.*foo/'
    filters = {'serve_path': valid_serve_path}
    assert filters == content_mgr.validate_list_filters(filters)
    invalid_serve_path = '*.txt'
    filters = {'serve_path': invalid_serve_path}
    with pytest.raises(ValueError) as exc:
        content_mgr.validate_list_filters(filters)
    assert 'invalid' in str(exc.value).lower()
