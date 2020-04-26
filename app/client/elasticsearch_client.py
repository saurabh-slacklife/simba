from elasticsearch import Elasticsearch

from app.config.config import ConfigType
import os
from app import logger


class ElasticSearchClient(object):

    def __init__(self, config: ConfigType):
        self.app_config = config

        if not (
                self.app_config and
                os.environ.get('ELASTIC_HOST')
        ):
            raise RuntimeError('Please set ELASTIC_HOST with Host in config %s', os.environ.get('ELASTIC_HOST'))

        logger.info(f'Config Object: {self.app_config}')
        self._elastic_connection: Elasticsearch = self.create_client()

    def create_client(self) -> Elasticsearch:
        elasticsearch_client = Elasticsearch(hosts=os.environ.get('ELASTIC_HOST'),
                                             connections=self.app_config['ELASTICSEARCH_CONNECTIONS'],
                                             dead_timeout=self.app_config['ELASTICSEARCH_DEAD_TIMEOUT'],
                                             timeout_cutoff=self.app_config['ELASTICSEARCH_TIMEOUT_CUTOFF'],
                                             sniff_on_start=True,
                                             sniff_on_connection_fail=True,
                                             sniffer_timeout=self.app_config['ELASTICSEARCH_SNIFFER_TIMEOUT'],
                                             request_timeout=self.app_config['ELASTICSEARCH_PER_REQUEST_TIMEOUT'],
                                             timeout=self.app_config['ELASTICSEARCH_TIMEOUT']
                                             )
        return elasticsearch_client

    @property
    def elastic_connection(self) -> Elasticsearch:
        return self._elastic_connection
