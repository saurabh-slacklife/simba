import logging
from app.config.config import ConfigType
from redis import Redis

from app.client.redis_client import RedisClient
from app.client.elasticsearch_client import ElasticSearchClient

logger = logging.getLogger('gunicorn.error')


class ClientService(object):
    def __init__(self, redis_client: RedisClient = None,
                 elastic_client: ElasticSearchClient = None,
                 config_object: ConfigType = None):
        self._redis_connection: Redis = None
        self._redis_client = redis_client
        self._elastic_client = elastic_client
        self._config_object = config_object

    def init_service(self, redis_client: RedisClient,
                     elastic_client: ElasticSearchClient,
                     config_object: ConfigType):
        self._redis_connection = redis_client.redis_connection
        self._elastic_client = elastic_client.elastic_connection
        self._config_object = config_object

    def register_client(self):
        pass

    def update_client(self):
        pass
