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
        elapsed = time.time() - self['initiated']
        return elapsed < self['duration']


class SessionManager(object):

    CTEXT_LENGTH = 64  # characters
    CDURATION = 30  # seconds

    ALLOWED_CHALLENGE_KEYS = ('id', 'text', 'duration', 'cipher', 'cipher_iv')
    REQUIRED_RESPONSE_PARAMS = ('id', 'encrypted_text')

    DEFAULT_DURATION = 3600  # seconds
    MAX_DURATION = 3600 * 24  # seconds

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
        return self._strip_handshake(handshake)

    def complete_handshake(self, client_name, response):
        client = self.client_manager.get_client(client_name)
        if not client:
            raise SessionException('No such client \'{}\''.format(
                client_name or ''))
        verified = self._verify_response(client, response)
        if not verified:
            raise SessionException('Handshake challenge response failed')
        duration = response.get('duration', self.DEFAULT_DURATION)
        session = self.create_session(client, duration)
        self.invalidate_handshake(client_name, response['id'])
        return session['token'], session['duration']

    def verify_session(self, client_name, session_token):
        client = self.client_manager.get_client(client_name)
        if not client:
            return False, 'No such client'
        session = self.load_session(client_name, session_token)
        if not session:
            return False, 'No session found'
        if not session.is_valid():
            return False, 'Session timedout'
        return True, 'Ok'

    def _verify_response(self, client, response):
        self._verify_response_params(response)
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
        return self.verify_ciphertext(handshake, response, client_key)

    def _verify_response_params(self, response):
        for key in self.REQUIRED_RESPONSE_PARAMS:
            if key not in response:
                msg = 'Response to auth handshake should contain {}'.format(
                    ', '.join(self.REQUIRED_RESPONSE_PARAMS))
                raise SessionException(msg)

    def create_handshake(self, client):
        handshake = TimedObject({
            'id': self.generate_cid(),
            'text': self.generate_ctext(),
            'duration': self.CDURATION,
            'client': client,
            'initiated': time.time(),
        })
        handshake.update(self.create_handshake_cipher())
        self.store_handshake(client, handshake)
        return handshake

    def create_handshake_cipher(self):
        return {
            'cipher': 'AES_CBC',
            'cipher_iv': aes_make_iv()
        }

    def create_session(self, client, duration):
        duration = min(duration, self.MAX_DURATION)
        session = TimedObject({
            'token': self.generate_session_token(),
            'client': client,
            'duration': duration,
            'initiated': time.time(),
        })
        self.store_session(client, session)
        return session

    def verify_ciphertext(self, handshake, response, key):
        plaintext = handshake['text']
        enc_iv = handshake['cipher_iv']
        client_enc_text = response['encrypted_text']
        server_enc_text = aes_encrypt(plaintext, key, enc_iv)
        return client_enc_text == server_enc_text

    def store_handshake(self, client, handshake):
        cid = handshake['id']
        self.handshakes[(client['name'], cid)] = handshake

    def load_handshake(self, client, handshake_id):
        return self.handshakes.get((client['name'], handshake_id))

    def invaidate_handshake(self, client_name, handshake_id):
        self.handshakes.pop((client_name, handshake_id), None)

    def generate_session_token(self):
        return uuid.uuid4().hex

    def store_session(self, client, session):
        token = session['token']
        self.sessions[(client['name'], token)] = session

    def load_session(self, client_name, token):
        return self.sessions.get((client_name, token))

    def generate_cid(self):
        return uuid.uuid4().hex

    def generate_ctext(self):
        bytes = os.urandom(self.CTEXT_LENGTH / 2)
        return binascii.hexlify(bytes)

    def cleanup(self):
        for key, handshake in self.handshakes.items():
            if not handshake.is_valid():
                self.invalidate_handshake(key)

        for key, session in self.sessions.items():
            if not session.is_valid():
                self.invalidate_session(key)

    def _strip_handshake(self, handshake):
        stripped_handshake = {}
        for key in self.ALLOWED_handshake_KEYS:
            stripped_handshake[key] = handshake[key]
        return stripped_handshake
