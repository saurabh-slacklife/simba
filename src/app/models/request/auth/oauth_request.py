from marshmallow import fields, Schema, RAISE, post_load, validates
from src.app.exception_handlers import BadRequestException


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
    grant_type = fields.String(required=True)
    code = fields.String(required=True)
    client_id = fields.String(required=True)
    client_secret = fields.String(required=True)
    redirect_uri = fields.String(required=True)

    class Meta:
        unknown = RAISE

    @validates("grant_type")
    def validate_grant_type(self, grant_type):
        if not grant_type and grant_type != 'authorization_code':
            raise BadRequestException(message={'message': 'Invalid Grant Type'})

    @post_load(pass_original=True)
    def oauth_session_post_load(self, data, **kwargs):
        return OAuthTokenRequest(**data, **kwargs)
