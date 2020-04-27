import urllib3
from urllib3 import HTTPConnectionPool


class HttpClient(object):
    def __init__(self, config=None):
        self.config = config
        self._http_connection_pool: HTTPConnectionPool = None
        self.init_app(config)

    def init_app(self, config):
        self.config = config
        self._create_connection_pool()

    def _create_connection_pool(self):
        headers = {}
        headers.setdefault('USER-AGENT', 'SIMBA APP')
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('Accept-Type', 'application/json')
        self._http_connection_pool = urllib3.HTTPConnectionPool(host=self.config.get('AUTHENTICATION_HOST'),
                                                                headers=headers,
                                                                block=True,
                                                                maxsize=self.config.get(
                                                                    'AUTHENTICATION_HOST_MAX_CONNECTIONS'))

    @property
    def get_connection(self):
        return self._http_connection_pool
