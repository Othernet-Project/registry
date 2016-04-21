# -*- coding: utf-8 -*-
"""
sessions.py: module for maintaining client sessions

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""


import os
import uuid
import binascii
import time

from .clients import ClientManager
from .crypto import aes_make_iv, aes_encrypt


class SessionException(Exception):
    pass


class TimedObject(dict):

    def is_valid(self):
        if 'initiated' in self and 'duration' in self:
            elapsed = time.time() - self['initiated']
            return 0 <= elapsed <= self['duration']
        return True


class SessionManager(object):

    HANDSHAKE_TEXT_LENGTH = 64  # characters
    HANDSHAKE_DURATION = 30  # seconds
    HANDSHAKE_CIPHER = 'AES_CBC'

    ALLOWED_CHALLENGE_KEYS = ('id', 'text', 'duration', 'cipher', 'cipher_iv')
    REQUIRED_RESPONSE_PARAMS = ('id', 'encrypted_text')

    SESSION_DEFAULT_DURATION = 3600  # seconds
    SESSION_MAX_DURATION = 3600 * 24  # seconds

    handshakes = {}
    sessions = {}

    def __init__(self, db):
        self.db = db
        self.client_manager = ClientManager(db)

    def start_handshake(self, client_name):
        client = self.client_manager.get_client(client_name)
        if not client:
            raise SessionException('No such client \'{}\''.format(
                client_name or ''))
        handshake = self.create_handshake(client)
        return self.strip_handshake(handshake)

    def complete_handshake(self, client_name, response):
        client = self.client_manager.get_client(client_name)
        if not client:
            raise SessionException('No such client \'{}\''.format(
                client_name or ''))
        if not self.validate_handshake_response(client, response):
            raise SessionException('Handshake challenge response failed')
        duration = self.calculate_session_duration(response)
        session = self._create_session(client, duration)
        self.invalidate_handshake(client_name, response['id'])
        return session['token'], session['duration']

    def create_handshake(self, client):
        handshake = TimedObject({
            'id': self.generate_handshake_id(),
            'text': self.generate_handshake_text(),
            'duration': self.HANDSHAKE_DURATION,
            'client': client,
            'initiated': time.time(),
            'cipher': self.HANDSHAKE_CIPHER,
            'cipher_iv': aes_make_iv()
        })
        self.store_handshake(client, handshake)
        return handshake

    def validate_handshake_response(self, client, response):
        self.validate_handshake_response_params(response)
        handshake = self.load_handshake(client, response['id'])
        if not handshake:
            raise SessionException('No matching handshake found for response')
        if not handshake.is_valid():
            raise SessionException('Handshake timedout')
        cipher = handshake['cipher']
        client_key = self.client_manager.get_client_keys(
            client['name']).get(cipher)
        if not client_key:
            raise SessionException(
                'Client does not have a key for cipher: {}'.format(cipher))
        return self.validate_ciphertext(handshake, response, client_key)

    def validate_handshake_response_params(self, response):
        for key in self.REQUIRED_RESPONSE_PARAMS:
            if key not in response:
                msg = 'Response to auth handshake should contain {}'.format(
                    ', '.join(self.REQUIRED_RESPONSE_PARAMS))
                raise SessionException(msg)

    def validate_ciphertext(self, handshake, response, key):
        plaintext = handshake['text']
        enc_iv = handshake['cipher_iv']
        client_enc_text = response['encrypted_text']
        server_enc_text = aes_encrypt(plaintext, key, enc_iv)
        return client_enc_text == server_enc_text

    def store_handshake(self, client, handshake):
        hid = handshake['id']
        self.handshakes[(client['name'], hid)] = handshake

    def load_handshake(self, client, handshake_id):
        return self.handshakes.get((client['name'], handshake_id))

    def invalidate_handshake(self, client_name, handshake_id):
        self.handshakes.pop((client_name, handshake_id), None)

    def _create_session(self, client, duration):
        session = TimedObject({
            'token': self.generate_session_token(),
            'client': client,
            'duration': duration,
            'initiated': time.time(),
        })
        self._store_session(client, session)
        return session

    def verify_session(self, client_name, session_token):
        client = self.client_manager.get_client(client_name)
        if not client:
            return False, 'No such client'
        session = self._load_session(client_name, session_token)
        if not session:
            return False, 'No session found'
        if not session.is_valid():
            return False, 'Session timedout'
        return True, 'Ok'

    def calculate_session_duration(self, handshake_response):
        requested_duration = int(
            handshake_response.get('duration', self.SESSION_DEFAULT_DURATION))
        duration = min(requested_duration, self.SESSION_MAX_DURATION)
        return duration

    def invalidate_session(self, client_name, session_token):
        self.sessions.pop((client_name, session_token), None)

    def _store_session(self, client, session):
        token = session['token']
        self.sessions[(client['name'], token)] = session

    def _load_session(self, client_name, token):
        return self.sessions.get((client_name, token))

    def generate_session_token(self):
        return uuid.uuid4().hex

    def generate_handshake_id(self):
        return uuid.uuid4().hex

    def generate_handshake_text(self):
        bytes = os.urandom(self.HANDSHAKE_TEXT_LENGTH / 2)
        return binascii.hexlify(bytes)

    def cleanup(self):
        count = 0
        for key, handshake in self.handshakes.items():
            if not handshake.is_valid():
                self.invalidate_handshake(*key)
                count += 1

        for key, session in self.sessions.items():
            if not session.is_valid():
                self.invalidate_session(*key)
                count += 1
        return count

    def strip_handshake(self, handshake):
        stripped_handshake = {}
        for key in self.ALLOWED_CHALLENGE_KEYS:
            if key in handshake:
                stripped_handshake[key] = handshake[key]
        return stripped_handshake
