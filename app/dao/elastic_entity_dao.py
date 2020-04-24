from elasticsearch_dsl import Document
from elasticsearch import Elasticsearch
from app import logger


class ElasticEntityDao(object):

    def __init__(self, es_connection: Elasticsearch):
        self.es_connection = es_connection

    def save(self, document: Document):
        """
        Saves the client_document in Elasticsearch. This should be override by the Document Dao

        :param document:
        :return:
        """
        return document.save(using=self.es_connection)

    def update(self, document: Document = None, *args):
        """
            Update the client_document in Elasticsearch. This should be override by the Document Dao

            :param document:
            :return:
        """
        return document.update(self.es_connection)

    def search_by_doc_id(self, document: Document = None, *args):
        """
            Search the client_document in Elasticsearch. This should be override by the Document Dao

            :param document:
            :return:
        """
        return document.search(self.es_connection)

    def delete_by_doc_id(self, document: Document = None, *args):
        """
        Delete the client_document in Elasticsearch. This should be override by the Document Dao

        :param document:
        :return:
        """
        return document.delete(using=self.es_connection)
