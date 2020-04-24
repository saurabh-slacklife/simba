from app.dao.elastic_entity_dao import ElasticEntityDao
from elasticsearch import Elasticsearch
from app.elastic_entities.client import ClientEntity
from app import logger

class EsClientDaoImp(ElasticEntityDao):
    def __init__(self, es_connection: Elasticsearch):
        self.es_connection = es_connection

    def save(self, client_document: ClientEntity):
        """
        Saves the document in Elasticsearch. This should be override by the Document Dao

        :param client_document:
        :return:
        """
        return super(EsClientDaoImp, self).save(using=self.es_connection, document=client_document)

    def update(self, client_document: ClientEntity, *args):
        """
            Update the client_document in Elasticsearch.

            :param document:
            :return:
        """
        return super(EsClientDaoImp, self).update(using=self.es_connection, document=client_document)

    def search_by_doc_id(self, client_document: ClientEntity, *args):
        """
            Search the client_document in Elasticsearch.

            :param document:
            :return:
        """
        return super(EsClientDaoImp, self).search_by_doc_id(using=self.es_connection, document=client_document)

    def delete_by_doc_id(self, client_document: ClientEntity, *args):
        """
        Delete the client_document in Elasticsearch.

        :param document:
        :return:
        """
        return super(EsClientDaoImp, self).delete_by_doc_id(using=self.es_connection, document=client_document)
