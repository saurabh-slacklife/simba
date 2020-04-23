import logging
from app.config.config import ConfigType
from redis import Redis

from app.client.redis_client import RedisClient

logger = logging.getLogger('gunicorn.error')


class ClientService(object):
    def __init__(self, redis_client: RedisClient = None, config_object: ConfigType = None):
        self._redis_connection: Redis = None
        self._redis_client = redis_client
        self._config_object = config_object

    def init_service(self, redis_client: RedisClient, config_object: ConfigType):
        self._redis_connection = redis_client.redis_connection
        self._config_object = config_object

    def register_client(self):
        pass

    def update_client(self):
        pass
