import functools

from marshmallow import fields, Schema, RAISE, post_load, validates

from app.exception_handlers import BadRequest


class GrantAuthRequest(Schema):
    response_type = fields.String(required=True)
    scope = fields.List(fields.String(required=True), required=True)
    client_id = fields.String(required=True)
    state = fields.String(required=True)

    class Meta:
        UNKNOWN = RAISE

    @post_load(pass_original=True)
    def oauth_grant_code_post_load(self, data, **kwargs):
        return GrantAuthRequest(**data, **kwargs)


class AuthTokenRequest(Schema):
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
            raise BadRequest(message={'message': 'Invalid Grant Type'})

    @post_load(pass_original=True)
    def oauth_session_post_load(self, data, **kwargs):
        return AuthTokenRequest(**data, **kwargs)


class RefreshTokenRequest(object):
    def __init__(self, refresh_token: str, client_id: str, client_secret: str):
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret


def field_validator(func):
    @functools.wraps(func)
    def func_wrapper(*args):
        invalid_key_dict = {}
        for key in args:
            if not key:
                invalid_key_dict.key = f'The {key} is Invalid'
        if len(invalid_key_dict) > 0:
            return False, invalid_key_dict
        else:
            return True

    return func_wrapper
