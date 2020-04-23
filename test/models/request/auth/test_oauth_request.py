from unittest import TestCase
from app.models.request.auth.oauth_request import RefreshTokenRequest


class TestRefreshTokenRequest(TestCase):

    def test_refresh_token(self):
        refresh_token_request = RefreshTokenRequest(refresh_token='refresh_token', client_id='client_id',
                                                    client_secret='client_secret')

        self.assertEqual(refresh_token_request.client_id, 'client_id', 'Assertion failed for Client Id')
        self.assertEqual(refresh_token_request.client_secret, 'client_secret', 'Assertion failed for Client Secret')
        self.assertEqual(refresh_token_request.refresh_token, 'refresh_token', 'Assertion failed for Refresh Token')

    def test_set_refresh_token(self):
        self.fail()

    def test_client_id(self):
        self.fail()

    def test_set_client_id(self):
        self.fail()

    def test_client_secret(self):
        self.fail()

    def test_set_client_secret(self):
        self.fail()
