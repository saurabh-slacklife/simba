from marshmallow import fields, Schema, RAISE, post_load


class OAuthGrantAuthRequest(Schema):
    response_type = fields.String(required=True)
    scope = fields.List(fields.String(required=True), required=True)
    client_id = fields.String(required=True)
    state = fields.String(required=True)

    class Meta:
        UNKNOWN = RAISE

    @post_load(pass_original=True)
    def oauth_grant_code_post_load(self, data, **kwargs):
        return OAuthGrantAuthRequest(**data, **kwargs)


class OAuthTokenRequest(Schema):
    code = fields.String(required=True)
    clientId = fields.String(required=True)
    clientSecret = fields.String(required=True)
    signingSecret = fields.String(required=True)

    class Meta:
        unknown = RAISE

    @post_load(pass_original=True)
    def oauth_session_post_load(self, data, **kwargs):
        return OAuthTokenRequest(**data, **kwargs)
