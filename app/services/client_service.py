from app import logger

from elasticsearch import Elasticsearch
from redis import Redis

from app.client.elasticsearch_client import ElasticSearchClient
from app.client.redis_client import RedisClient
from app.config.config import ConfigType
from app.dao.es_client_dao_impl import EsClientDaoImp
from app.elastic_entities.client import ClientEntity
from app.exception_handlers import RequestConflict


class ClientService(object):
    def __init__(self):
        self._redis_connection: Redis = None
        self._elastic_connection: Elasticsearch = None
        self._config_object = None
        self.client_dao: EsClientDaoImp = None

    def init_service(self, redis_client: RedisClient,
                     elastic_client: ElasticSearchClient,
                     config_object: ConfigType):
        self._redis_connection = redis_client.redis_connection
        self._elastic_connection: Elasticsearch = elastic_client.elastic_connection
        self._config_object = config_object
        self.client_dao = EsClientDaoImp(self._elastic_connection)

    def search(self, email: str, contact_number: str):

        if email and contact_number:
            return self.client_dao.search_by_email_and_contact_number(email=email, contact_number=contact_number)
        elif email:
            return self.client_dao.search_by_email(email)
        else:
            return self.client_dao.search_by_contact_number(contact_number=contact_number)

    def update(self):
        pass

    def register(self, client_entity: ClientEntity):

        response_list = self.client_dao.search_by_email_or_contact_number(email=client_entity.email,
                                                                          contact_number=client_entity.contact_number)

        if response_list and len(response_list) > 0:
            raise RequestConflict(message={'message': 'Client already exists with similar email or contact number'})
        else:
            doc_status, doc_meta = self.client_dao.save(client_entity)
            logger.info(f'Persisted - doc_status: {doc_status} and doc_meta: {doc_meta}')
            return doc_status, doc_meta
