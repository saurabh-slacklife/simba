import logging
from app.config.config import ConfigType
from redis import Redis
from app.dao.es_client_dao_impl import EsClientDaoImp
from app.client.redis_client import RedisClient
from app.client.elasticsearch_client import ElasticSearchClient
from app.elastic_entities.client import ClientEntity

logger = logging.getLogger('gunicorn.error')


class ClientService(object):
    def __init__(self):
        self._redis_connection = None
        self._elastic_connection = None
        self._config_object = None
        self.client_dao = None

    def init_service(self, redis_client: RedisClient,
                     elastic_client: ElasticSearchClient,
                     config_object: ConfigType):
        self._redis_connection = redis_client.redis_connection
        self._elastic_connection = elastic_client.elastic_connection
        self._config_object = config_object
        self.client_dao = EsClientDaoImp(self._elastic_connection)

    def register_client(self):
        pass

    def update_client(self):
        pass

    def create_client(self, client_entity: ClientEntity):
        logger.info(f'Valid request: {client_entity}')
        doc_status, doc_meta = client_entity.save(using=self._elastic_connection)

        logger.info(f'Persisted - doc_status: {doc_status} and doc_meta: {doc_meta}')

        return doc_status, doc_meta
