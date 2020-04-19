from marshmallow import fields, Schema, RAISE, post_load


class AuthSession(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)
    token_type = fields.String(required=True)
    expires = fields.Integer(required=True)

    class Meta:
        unknown = RAISE

    @post_load
    def auth_session_post_load(self, data, **kwargs):
        return AuthSession(**data)
