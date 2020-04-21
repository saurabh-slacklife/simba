class OAuthTokenResponse(object):
    def __init__(self, access_token: str, refresh_token: str,
                 token_type: str, expires: int):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires = expires
