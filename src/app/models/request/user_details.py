from marshmallow import Schema, fields, RAISE, post_load


class UserDetails(Schema):
    first_name = fields.String(required=True,
                               error_messages={"required": {"message": "first_name required", "code": 400}})
    last_name = fields.String(required=True,
                              error_messages={"required": {"message": "last_name required", "code": 400}})
    email = fields.Email(required=True,
                         error_messages={"required": {"message": "email required", "code": 400}})
    country_code = fields.String(required=True,
                                 error_messages={"required": {"message": "country_code required", "code": 400}})
    contact_number = fields.String(required=True,
                                   error_messages={"required": {"message": "contact_number required", "code": 400}})

    class Meta:
        unknown = RAISE

    @post_load
    def create_user_detail_post_load(self, data, **kwargs):
        return UserDetails(**data)
