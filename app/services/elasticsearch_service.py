from elasticsearch.client import Elasticsearch as es
from app.config.config import ConfigType
from app import logger


class ElasticSearchService(object):
    def __init__(self, es_client=None, config_object: ConfigType = None):
        self._es_connection: es = None
        self._es_client = es_client
        self._config_object = config_object

    def init_service(self, es_client, config_object: ConfigType):
        self._es_connection = es_client.redis_connection
        self._config_object = config_object
