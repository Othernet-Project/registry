# -*- coding: utf-8 -*-
"""
auth.py: module for authenticating and authorizing clients

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging

from bottle import request


from .sessions import SessionManager, SessionException


def get_session_manager():
    config = request.app.config
    db = request.db.registry
    return SessionManager(config=config, db=db)


def start_handshake():
    params = request.forms
    client_name = params.get('client_name')
    sessions = get_session_manager()
    try:
        challenge = sessions.start_handshake(client_name)
        return {'success': True, 'challenge': challenge}
    except SessionException as exc:
        return {'success': False, 'message': str(exc)}
    except Exception as exc:
        logging.exception(
            'Client handshake failed with unknown exception: {}'.format(exc))
        return {'success': False, 'message': 'Unknown Error'}


def verify_response():
    params = request.forms
    client_name = params.get('client_name')
    sessions = get_session_manager()
    try:
        session_token, duration = sessions.complete_handshake(client_name,
                                                              params)
        return {
            'success': True,
            'session': {'token': session_token, 'duration': duration}
        }
    except SessionException as exc:
        return {'success': False, 'message': str(exc)}
    except Exception as exc:
        logging.exception(
            'Client handshake failed with unknown exception: {}'.format(exc))
        return {'success': False, 'message': 'Unknown Error'}
