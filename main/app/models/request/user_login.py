from marshmallow import Schema, fields, post_load, validate, RAISE


class UserLoginModel(Schema):
    email = fields.String(required=True, error_messages={"required": {"message": "email required", "code": 400}})
    password = fields.Email(required=True, validate=validate.Length(min=8),
                            error_messages={"required": {
                                "message": "password required and should have minimum length of 8 characters",
                                "code": 400}})

    @post_load
    def user_login_post_load(self, data, **kwargs):
        return UserLoginModel(**data)

    class Meta:
        unknown = RAISE
