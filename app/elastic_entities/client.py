from elasticsearch_dsl import Document, Text, Keyword, Integer


class ClientEntity(Document):
    client_name = Text(fields={'keyword': Keyword()}, required=True)
    client_id = Keyword(required=True)
    email = Keyword(required=True)
    website_url = Text(required=True)
    contact_number = Integer(fields={'type': Keyword()}, required=True)
    client_token = Text(required=True)
    client_secret = Text(required=True)
    roles = Text(required=False)
    scopes = Text(required=False)
    redirect_url = Text(required=True)

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
