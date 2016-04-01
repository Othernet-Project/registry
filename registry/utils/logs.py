# -*- coding: utf-8 -*-
"""
logs.py: utility methods for logs

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import sys
import logging.config


def configure_logging(config):
    logging.config.dictConfig({
        'version': 1,
        'root': {
            'handlers': ['file', 'console'],
            'level': config.get('logging.level', logging.DEBUG),
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': config['logging.output'],
                'maxBytes': config['logging.size'],
                'backupCount': config['logging.backups'],
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': logging.INFO,
                'stream': sys.stdout
            }
        },
        'formatters': {
            'default': {
                'format': config['logging.format'],
                'datefmt': config['logging.date_format'],
            },
        },
    })
