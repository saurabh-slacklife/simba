from redis import BlockingConnectionPool, Connection
from redis import Redis

from main.app.config.config import BaseConfig
import os


class RedisClient(object):
    def __init__(self, config=None):
        self.config = config

        if not (
                self.config and
                os.environ.get('REDIS_HOST')
        ):
            raise RuntimeError('Please set REDIS_HOST with Host in config %s', os.environ.get('REDIS_HOST'))

        self._redis_connection = self.init_redis()

    def init_redis(self):
        connection_pool = self.__create_connection_pool__()
        return Redis(connection_pool=connection_pool)

    # TODO Change the access of Baseconfig, it should just hold the Variable names to be taken from config
    def __create_connection_pool__(self) -> BlockingConnectionPool:
        connection_class = Connection(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT', 6379),
                                      db=self.config.get('REDIS_DB', 0),
                                      username=self.config.get('REDIS_USERNAME', None),
                                      password=os.environ.get('REDIS_PASSWORD', None),
                                      socket_timeout=BaseConfig.REDIS_SOCKET_TIMEOUT,
                                      socket_connect_timeout=BaseConfig.REDIS_SOCKET_CONNECT_TIMEOUT,
                                      socket_keepalive=BaseConfig.REDIS_SOCKET_KEEP_ALIVE,
                                      health_check_interval=BaseConfig.REDIS_HEALTH_CHECK_INTERVAL,
                                      client_name=BaseConfig.REDIS_CLIENT_NAME)

        pool = BlockingConnectionPool(onnection_class=connection_class,
                                      timeout=BaseConfig.REDIS_CONNECTION_TIMEOUT,
                                      max_connections=BaseConfig.REDIS_MAX_CONNECTION)
        return pool

    @property
    def redis_connection(self) -> Redis:
        if self._redis_connection:
            return self._redis_connection
        else:
            raise RuntimeError(
                f'Redis Connection used before initializing.'
                f'Use: RedisClient(app) or rediClient.init_redis(app) to initialize')
