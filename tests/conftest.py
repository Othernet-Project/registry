import os
import sys
import time
import httplib
import multiprocessing

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

import pytest
try:
    from unittest import mock
except ImportError:
    import mock

from squery_lite.pytest_fixtures import *


TESTDIR = os.path.abspath(os.path.dirname(__file__))
DATADIR = os.path.join(TESTDIR, 'data')


class TestClient:

    def __init__(self, host='127.0.0.1', port=8080):
        self.conn = httplib.HTTPConnection(host, port, timeout=200)

    def request(self, method, url, body=None, headers={}):
        self.conn.connect()
        self.conn.request(method, url, body, headers)
        resp = self.conn.getresponse()
        return resp

    def get(self, url, headers={}):
        return self.request('GET', url, headers=headers)

    def post(self, url, data={}, headers={}):
        return self.request('POST', url, body=urlencode(data), headers=headers)

    def delete(self, url, headers={}):
        return self.request('DELETE', url, headers=headers)

    def patch(self, url, data={}, headers={}):
        return self.request('PATCH', url, body=urlencode(data),
                            headers=headers)

    def put(self, url, data={}, headers={}):
        return self.request('PUT', url, body=urlencode(data), headers=headers)


class TestServer:

    def __init__(self):
        self.server_process = None

    def start(self):
        from registry.app import main
        self.server_process = multiprocessing.Process(target=main)
        self.server_process.start()
        time.sleep(1.0)
        print('Starting server')

    def stop(self):
        if not self.server_process:
            return
        self.server_process.terminate()
        print('Stopping server')


@pytest.fixture
def http_client():
    return TestClient


@pytest.fixture(scope='session')
def database_config():
    return {
        'path': 'tests/tmp',
        'databases': [
            {'name': 'registry',
             'migrations': 'registry.migrations.registry'}
        ],
        'conf': {},
    }


@pytest.fixture
def populated_databases(databases):
    for data_file in os.listdir(DATADIR):
        if not data_file.endswith(".sql"):
            continue
        path = os.path.join(DATADIR, data_file)
        with open(path) as fobj:
            dbname = os.path.splitext(data_file)[0]
            db = getattr(databases, dbname)
            db.executescript(fobj.read())
    return databases


@pytest.yield_fixture
def server(populated_databases):
    testargv = ['/usr/bin/env', 'python', '--conf',
                os.path.join(DATADIR, 'test-config.ini')]
    with mock.patch.object(sys, 'argv', testargv), mock.patch('registry.utils.databases.init_databases', lambda *args, **kwargs: populated_databases):
        server = TestServer()
        try:
            yield server.start
        finally:
            server.stop()
