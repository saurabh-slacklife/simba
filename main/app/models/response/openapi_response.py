from marshmallow import Schema, fields, validates, post_load, RAISE


class OpenApiResponse(Schema):
    rel = fields.String(required=True, error_messages={"required": {"message": "rel required", "code": 400}})
    uri = fields.String(required=True, error_messages={"required": {"message": "uri required", "code": 400}})
    action = fields.String(required=True, error_messages={"required": {"message": "action required", "code": 400}})
    types = fields.String(many=True, required=True,
                          error_messages={"required": {"message": "types required", "code": 400}})

    class Meta:
        unknown = RAISE

    @post_load
    def openapi_response__post_load(self, data, **kwargs):
        return OpenApiResponse(**data)
