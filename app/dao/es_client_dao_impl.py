from elasticsearch import Elasticsearch

from app import logger
from typing import List
from app.dao.elastic_entity_dao import ElasticEntityDao
from app.dao.es_query_templates import search_client_by_contact_number_template, search_client_by_email_template, search_client_by_id_template
from app.dao.es_query_templates import search_client_by_email_and_contact_number_template, search_client_by_email_or_contact_number_template
from app.elastic_entities.client import ClientEntity


class EsClientDaoImp(ElasticEntityDao):
    PARAMS = {'request_cache': 'true'}

    def __init__(self, es_connection: Elasticsearch):
        self.es_connection = es_connection

    def save(self, client_document: ClientEntity):
        """
        Saves the document in Elasticsearch. This should be override by the Document Dao

        :param client_document:
        :return:doc_status, doc_meta
        """
        doc_status, doc_meta = super(EsClientDaoImp, self).save(es_connection=self.es_connection,
                                                                document=client_document)
        return doc_status, doc_meta

    def update(self, client_document: ClientEntity, *args):
        """
            Update the client_document in Elasticsearch.

            :param client_document:
            :param document:
            :return: doc_status, doc_meta
        """
        return super(EsClientDaoImp, self).update(es_connection=self.es_connection, document=client_document)

    def search_by_id(self, client_id: str):

        """
            Search the document by Client ID in Elasticsearch. If exists - returns document else 0
            :param client_id:
            :return:source
        """

        response = self.es_connection.search(index=ClientEntity.Index.name,
                                             body=search_client_by_id_template(client_id=client_id),
                                             params=self.PARAMS)

        return self.__parse_response__(response)

    def search_by_email(self, email):

        """
            Search the document by Email in Elasticsearch. If exists - returns document else 0
            :param email:
            :return:source
        """

        response = self.es_connection.search(index=ClientEntity.Index.name,
                                             body=search_client_by_email_template(email=email),
                                             params=self.PARAMS)

        return self.__parse_response__(response)

    def search_by_email_and_contact_number(self, email, contact_number):
        """
         Search the document by Email and Contact Number in Elasticsearch. If exists - returns document else 0
           :param contact_number:
           :param email:
           :return:source
        """

        response = self.es_connection.search(index=ClientEntity.Index.name,
                                             body=search_client_by_email_and_contact_number_template(email=email,
                                                                                                     contact_number=contact_number),
                                             params=self.PARAMS)

        return self.__parse_response__(response)

    def search_by_contact_number(self, contact_number):
        """
          Search the document by Contact Number in Elasticsearch. If exists - returns document else 0
          :param contact_number:
          :return:source
        """

        response = self.es_connection.search(index=ClientEntity.Index.name,
                                             body=search_client_by_contact_number_template(contact_number=contact_number),
                                             params=self.PARAMS)

        return self.__parse_response__(response)

    def search_by_email_or_contact_number(self, email, contact_number):
        """
            Search the document by Email or Contact Number in Elasticsearch. If exists - returns document else 0
            :param contact_number:
            :param email:
            :return:source
        """
        response = self.es_connection.search(index=ClientEntity.Index.name,
                                             body=search_client_by_email_or_contact_number_template(email=email,
                                                                                                    contact_number=contact_number),
                                             params=self.PARAMS)

        return self.__parse_response__(response)

    def __parse_response__(self, response):
        hit_count = response.get('hits').get('total').get('value')
        if hit_count > 0:
            response_list = []
            hits = response.get('hits').get('hits')
            for hit in hits:
                response_list.append(hit.get('_source'))
            return response_list
        else:
            return 0
