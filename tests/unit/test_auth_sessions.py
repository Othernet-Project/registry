# -*- coding: utf-8 -*-
"""
test_auth_sessions.py: Unit tests for registry.auth.sessions module

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals

from datetime import datetime

import pytest
try:
    from unittest import mock
except ImportError:
    import mock

from registry.auth import sessions as mod


@pytest.fixture
def session_mgr():
    db = mock.MagicMock
    return mod.SessionManager(db)


BASE_TIMESTAMP = (datetime(2016, 4, 19) - datetime(1970, 1, 1)).total_seconds()


def test_timed_object_is_valid_no_duration():
        to = mod.TimedObject({
            'random_key1': 0,
            'duration': 10,
        })
        assert to.is_valid()
        to = mod.TimedObject({
            'initiated': 0,
            'random_key2': 0
        })
        assert to.is_valid()


@pytest.mark.parametrize('initiated,duration,current,valid', [
    (BASE_TIMESTAMP, 10, BASE_TIMESTAMP, True),
    (BASE_TIMESTAMP, 10, BASE_TIMESTAMP + 5, True),
    (BASE_TIMESTAMP, 10, BASE_TIMESTAMP + 11, False),
    (BASE_TIMESTAMP, 10, BASE_TIMESTAMP - 1, False)
])
def test_timed_object_is_valid(initiated, duration, current, valid):
    mock_time = mock.Mock()
    mock_time.return_value = current
    with mock.patch('time.time', mock_time):
        to = mod.TimedObject({
            'initiated': initiated,
            'duration': duration
        })
        assert to.is_valid() == valid


def test_session_mgr_start_handshake_required_params(session_mgr):
    client = {'name': 'test_client'}
    handshake = session_mgr.create_handshake(client)
    received_params = set(handshake.keys())
    expected_params = set(('id', 'text', 'duration', 'cipher'))
    assert expected_params.issubset(received_params)


def test_session_mgr_create_session_required_params(session_mgr):
    client = {'name': 'test_client'}
    duration = 3600
    session = session_mgr._create_session(client, duration)
    received_params = set(session.keys())
    expected_params = set(('token', 'duration'))
    assert expected_params.issubset(received_params)


def test_session_mgr_strip_handshake(session_mgr):
    valid = {
        'id': 'id123',
        'text': 'test message',
        'cipher': 'AES_CBC',
    }
    invalid = {
        'invalid_key1': 'val1',
        'id2': 'id123',
        'another_invalid': 'foobar'
    }
    data = valid.copy()
    data.update(invalid)
    result = session_mgr.strip_handshake(data)
    assert set(result.keys()) == set(valid.keys())
    assert set(result.values()) == set(valid.values())
