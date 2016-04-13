# -*- coding: utf-8 -*-
"""
crypto.py: utility methods for cryptography

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from Crypto.Cipher import AES


def aes_make_iv():
    return 'This is an IV456'


def aes_encrypt(message, key, iv):
    if not isinstance(message, bytes):
        raise TypeError('message must be a byte string')
    if not isinstance(message, bytes):
        raise TypeError('key must be a byte string')
    if not isinstance(message, bytes):
        raise TypeError('message must be a byte string')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(message)
