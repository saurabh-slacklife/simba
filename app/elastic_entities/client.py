from elasticsearch_dsl import Document, Text, Keyword, Nested


class ClientEntity(Document):
    client_name = Text(fields={'keyword': Keyword()}, required=True)
    client_id = Text(fields={'keyword': Keyword()}, required=True)
    client_token = Text(fields={'Keyword': Keyword()}, required=True)
    client_secret = Text(fields={'Keyword': Keyword()}, required=True)
    roles = Nested(Text(), required=True)
    scopes = Nested(Text(), required=True)

    class Index:
        name = 'client-test'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    def save(self, validate=True, skip_empty=True, **kwargs):
        doc_status = super(ClientEntity, self).save(**kwargs)
        doc_meta = self.meta
        return doc_status, doc_meta
