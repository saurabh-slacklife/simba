from marshmallow import fields, Schema, RAISE, post_load


class OAuthTokenRequest(Schema):
    code = fields.String(required=True)
    clientId = fields.String(required=True)
    clientSecret = fields.String(required=True)
    signingSecret = fields.String(required=True)

    class Meta:
        unknown = RAISE

    @post_load
    def oauth_session_post_load(self, data, **kwargs):
        return OAuthTokenRequest(**data)
