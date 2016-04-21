import httplib


try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

import pytest


class TestClient:

    def __init__(self, host='127.0.0.1', port=8080):
        self.conn = httplib.HTTPConnection(host, port, timeout=200)

    def request(self, method, url, body=None, headers={}):
        self.conn.connect()
        self.conn.request(method, url, body, headers)
        resp = self.conn.getresponse()
        self.conn.close()
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


@pytest.fixture
def http_client():
    return TestClient()


@pytest.fixture(scope='session')
def database_config():
    return {
        'path': 'tmp/tests/',
        'databases': [
            {'name': 'registry',
             'migrations': 'registry.migrations.registry'}
        ],
        'conf': {},
    }
