from marshmallow import fields, Schema, RAISE, post_load


class OAuthTokenResponse(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)
    token_type = fields.String(required=True)
    expires = fields.Integer(required=True)

    class Meta:
        unknown = RAISE

    @post_load
    def oauth_token_post_load(self, data, **kwargs):
        return OAuthTokenResponse(**data)
