from json import JSONEncoder
import json


class OpenApiResponse(object):
    def __init__(self, rel: str, uri: str, action: str, types: str):
        self.rel = rel
        self.uri = uri
        self.action = action
        self.types = types

    @property
    def get_uri(self):
        return self.uri

    @property
    def get_rel(self):
        return self.rel

    @property
    def get_action(self):
        return self.action

    @property
    def get_types(self):
        return self.types


class OpenApiResponseEncoder(JSONEncoder):
    def default(self, o: OpenApiResponse) -> OpenApiResponse:
        if isinstance(o, OpenApiResponse):
            return o.__dict__
        else:
            json.JSONEncoder.default(self, o)
