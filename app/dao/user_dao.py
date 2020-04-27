from elasticsearch import Elasticsearch

from app.dao.elastic_entity_dao import ElasticEntityDao
from app.dao.es_query_templates import search_user_by_id_template
from app.elastic_entities.user import UserEntity


class UserDaoImp(ElasticEntityDao):
    PARAMS = {'request_cache': 'true'}

    def __init__(self, es_connection: Elasticsearch):
        self.es_connection = es_connection

    def save(self, user_document: UserEntity):
        """
        Saves the document in Elasticsearch. This should be override by the Document Dao

        :param user_document:
        :return:doc_status, doc_meta
        """
        doc_status, doc_meta = super(UserDaoImp, self).save(es_connection=self.es_connection,
                                                            document=user_document)
        return doc_status, doc_meta

    def update(self, user_document: UserEntity, *args):
        """
            Update the client_document in Elasticsearch.

            :param client_user_documentdocument:
            :param document:
            :return: doc_status, doc_meta
        """
        return super(UserDaoImp, self).update(es_connection=self.es_connection, document=user_document)

    def search_by_id(self, user_id: str):
        """
            Search the document by User ID in Elasticsearch. If exists - returns document else 0
            :param user_id:
            :return:source
        """

        response = self.es_connection.search(index=UserDaoImp.Index.name,
                                             body=search_user_by_id_template(client_id=user_id),
                                             params=self.PARAMS)

        return self.__parse_response__(response)
