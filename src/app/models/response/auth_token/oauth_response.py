from json import JSONEncoder
import json


class AuthTokenResponse(object):
    def __init__(self, access_token: str, refresh_token: str,
                 token_type: str, expires: int):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires = expires


class AuthTokenResponseEncoder(JSONEncoder):
    def default(self, o: AuthTokenResponse) -> AuthTokenResponse:
        if isinstance(o, AuthTokenResponse):
            return o.__dict__
        else:
            json.JSONEncoder.default(self, o)
