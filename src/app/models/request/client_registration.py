from marshmallow import Schema, fields, post_load, validate, RAISE


class ClientApp(Schema):
    type = fields.String(required=True, error_messages={
        "required": {"message": "type is required. Possible values: Web Application, Native Apps", "code": 400}})
    name = fields.String(required=True, error_messages={
        "required": {"message": "name is required.", "code": 400}})
    description = fields.String(required=True, validate=validate.Length(max=120), error_messages={
        "required": {"message": "description is required.", "code": 400}})
    website = fields.Url(required=True, schemes='https', relative=False)
    email = fields.List(fields.Email(required=True, error_messages={
        "required": {"message": "Invalid email.", "code": 400}}))
    redirectUri = fields.String(required=True)

    class Meta:
        unknown = RAISE

    @post_load
    def register_client_post_load(self, data, **kwargs):
        return ClientApp(**data)
