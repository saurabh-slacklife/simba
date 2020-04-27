from app import logger
from datetime import datetime as dt
from elasticsearch import Elasticsearch
from redis import Redis

from app.client.elasticsearch_client import ElasticSearchClient
from app.client.redis_client import RedisClient
from app.config.config import ConfigType
from app.dao.user_dao import UserDaoImp
from app.elastic_entities.user import UserEntity
from app.exception_handlers import RequestConflict
from hashlib import sha256, md5


class UserService(object):
    def __init__(self, redis_connection: Redis = None,
                 elastic_client: ElasticSearchClient = None,
                 config_object=None):
        self._redis_connection = redis_connection
        self._elastic_connection: Elasticsearch = elastic_client.elastic_connection
        self._config_object = config_object
        self.client_dao: UserDaoImp = None

    def init_service(self, redis_client: RedisClient,
                     elastic_client: ElasticSearchClient,
                     config_object: ConfigType):
        self._redis_connection = redis_client.redis_connection
        self._elastic_connection: Elasticsearch = elastic_client.elastic_connection
        self._config_object = config_object
        self.client_dao = UserDaoImp(self._elastic_connection)

    def search(self, user_id: str):
        if user_id:
            return self.client_dao.search_by_id(user_id=user_id)
