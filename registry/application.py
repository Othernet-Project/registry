# -*- coding: utf-8 -*-
"""
app.py: main module

Copyright 2014-2016, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals

import os
import gevent
import logging
import importlib

from bottle import Bottle
from gevent import pywsgi
from confloader import get_config_path, ConfDict

from .utils.logs import configure_logging
from .utils.system import on_interrupt


class Application(object):
    DEFAULT_CONFIG_FILENAME = 'config.ini'
    CONFIG_DEFAULTS = {
        'catchall': True,
        'autojson': True
    }

    LOOP_INTERVAL = 5  # seconds

    def __init__(self, root_dir):
        self.server = None
        self.app = Bottle()
        self.background_hooks = []
        self.stop_hooks = []

        # Configure the application
        self._configure(root_dir)

        # Register application hooks
        self.pre_init(self.config['stack.pre_init'])
        self.add_plugins(self.config['stack.plugins'])
        self.add_routes(self.config['stack.routes'])
        self.add_background(self.config['stack.background'])
        self.add_stop_hooks(self.config['stack.pre_stop'])

        # Register interrupt handler
        on_interrupt(self.stop)

    def _configure(self, root_dir):
        default_path = os.path.join(root_dir, self.DEFAULT_CONFIG_FILENAME)
        self.config_path = get_config_path(default=default_path)
        config = ConfDict.from_file(self.config_path,
                                    defaults=self.CONFIG_DEFAULTS)
        config['root_dir'] = root_dir
        self.config = self.app.config = config
        configure_logging(self.config)

    def pre_init(self, pre_init):
        for hook in pre_init:
            hook = self._import(hook)
            hook(self.config)

    def add_plugins(self, plugins):
        for plugin in plugins:
            plugin = self._import(plugin)
            self.app.install(plugin(self.config))

    def add_routes(self, routing):
        for route in routing:
            route = self._import(route)
            for r in route(self.config):
                path, method, cb, name, kw = r
                self.app.route(path, method, cb, name=name, **kw)

    def add_background(self, background_calls):
        for hook in background_calls:
            hook = self._import(hook)
            self.background_hooks.append(hook)

    def add_stop_hooks(self, pre_stop):
        for hook in pre_stop:
            hook = self._import(hook)
            self.stop_hooks.append(hook)

    def start(self):
        host = self.config['server.host']
        port = self.config['server.port']
        self.server = pywsgi.WSGIServer((host, port), self.app, log=None)
        self.server.start()
        assert self.server.started, 'Expected server to be running'
        logging.info('Started server on http://{host}:{port}'.format(
            host=host, port=port))
        self._init_background()

    def _init_background(self):
        while True:
            gevent.sleep(self.LOOP_INTERVAL)
            for hook in self.background_hooks:
                try:
                    hook(self.app)
                except:
                    logging.exception('Error while running background hook')

    def stop(self):
        logging.info('Stopping the application')
        self.server.stop(5)
        logging.info('Running pre-stop hooks')
        for hook in self.stop_hooks:
            try:
                hook(self.app)
            except:
                logging.exception('Error while running pre-stop hook')

    @staticmethod
    def _import(name):
        mod, obj = name.rsplit('.', 1)
        mod = importlib.import_module(mod)
        return getattr(mod, obj)
