from app import logger
from datetime import datetime as dt
from elasticsearch import Elasticsearch
from redis import Redis

from app.client.elasticsearch_client import ElasticSearchClient
from app.client.redis_client import RedisClient
from app.config.config import ConfigType
from app.dao.es_client_dao_impl import EsClientDaoImp
from app.elastic_entities.client import ClientEntity
from app.exception_handlers import RequestConflict
from hashlib import sha256, md5


class ClientService(object):
    def __init__(self, redis_connection: Redis = None,
                 config_object=None):
        self._redis_connection = redis_connection
        self._elastic_connection = None
        self._config_object = config_object
        self.client_dao: EsClientDaoImp = None

    def init_service(self, redis_client: RedisClient,
                     elastic_client: ElasticSearchClient,
                     config_object: ConfigType):
        self._redis_connection = redis_client.redis_connection
        self._elastic_connection: Elasticsearch = elastic_client.elastic_connection
        self._config_object = config_object
        self.client_dao = EsClientDaoImp(self._elastic_connection)

    def search(self, email: str, contact_number: int):

        if email and contact_number:
            return self.client_dao.search_by_email_and_contact_number(email=email, contact_number=contact_number)
        elif email:
            return self.client_dao.search_by_email(email)
        elif contact_number:
            return self.client_dao.search_by_contact_number(contact_number=contact_number)

    def update(self):
        pass

    def register(self, client_entity: ClientEntity):

        response_list = self.client_dao.search_by_email_or_contact_number(email=client_entity.email,
                                                                          contact_number=client_entity.contact_number)

        if response_list and len(response_list) > 0:
            raise RequestConflict(message={'message': 'Client already exists with similar email or contact number'})
        else:
            self.generate_hashes(client_entity)

            doc_status, doc_meta = self.client_dao.save(client_entity)
            logger.info(f'Persisted - doc_status: {doc_status} and doc_meta: {doc_meta}')
            return doc_status, doc_meta

    def generate_hashes(self, client_entity):
        id_hash_string = f'{client_entity.email}:{client_entity.contact_number}'
        client_id = sha256(id_hash_string.encode('utf-8')).hexdigest()
        token_hash_string = f'{id_hash_string}:{dt.utcnow()}'
        client_token = sha256(token_hash_string.encode('utf-8')).hexdigest()
        secret_md5_string = f'{client_token}:{dt.utcnow()}'
        client_secret = md5(secret_md5_string.encode('utf-8')).hexdigest()
        client_entity.client_id = client_id
        client_entity.client_token = client_token
        client_entity.client_secret = client_secret
