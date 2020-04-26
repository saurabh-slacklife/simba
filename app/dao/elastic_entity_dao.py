from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document


class ElasticEntityDao(object):

    def save(self, es_connection: Elasticsearch, document: Document):
        """
        Saves the client_document in Elasticsearch. This should be override by the Document Dao

        :param es_connection:
        :param document:
        :return: doc_status, doc_meta
        """
        return document.save(using=es_connection)

    def update(self, es_connection: Elasticsearch, document: Document = None, *args):
        """
            Update the client_document in Elasticsearch. This should be override by the Document Dao

            :param es_connection:
            :param document:
            :return: doc_status, doc_meta
        """
        return document.update(using=es_connection)

    def search_by_doc_id(self, es_connection: Elasticsearch, document: Document = None, *args):
        """
            Search the client_document in Elasticsearch. This should be override by the Document Dao

            :param es_connection:
            :param document:
            :return: doc_status, doc_meta
        """
        return document.search(using=es_connection)

    def delete_by_doc_id(self, es_connection: Elasticsearch, document: Document = None, *args):
        """
        Delete the client_document in Elasticsearch. This should be override by the Document Dao

        :param es_connection:
        :param document:
        :return: doc_status, doc_meta
        """
        return document.delete(using=es_connection)

    def search_by_email(self, email):
        """
            Search the document by Email in Elasticsearch. This should be override by the Document Dao
            :param email:
            :return:source
        """
        pass
