from elasticsearch_dsl import Document, Text, Keyword


class UserEntity(Document):
    user_id = Keyword(required=True)
    roles = Text(required=False)
    scopes = Text(required=False)
    clients = Keyword(required=True)

    class Index:
        name = 'user-test'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    def save(self, validate=True, skip_empty=True, **kwargs):
        doc_status = super(UserEntity, self).save(**kwargs)
        doc_meta = self.meta
        return doc_status, doc_meta
