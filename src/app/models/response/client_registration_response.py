from marshmallow import Schema, fields, validate, RAISE, post_load


class ClientRegisterResponse(Schema):
    appId = fields.String(required=True)
    clientId = fields.String(required=True)
    clientSecret = fields.String(required=True)
    signingSecret = fields.String(required=True)

    class Meta:
        UNKNOWN = RAISE

    @post_load
    def client_app_response_post_load(self, data, **kwargs):
        return ClientRegisterResponse(**data)
