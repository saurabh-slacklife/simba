from unittest import TestCase
import os


class TestRefreshTokenRequest(TestCase):

    def setUp(self):
        os.environ['SERVICE_ENV'] = 'dev'

    def test_refresh_token(self):
        from app.models.request.auth.oauth_request import RefreshTokenRequest
        os.environ.__setattr__('SERVICE_ENV', 'dev')
        refresh_token_request = RefreshTokenRequest(refresh_token='refresh_token', client_id='client_id',
                                                    client_secret='client_secret')
        assert refresh_token_request.client_id == 'client_id'
        assert refresh_token_request.client_secret == 'client_secret'
        assert refresh_token_request.refresh_token == 'refresh_token'
        refresh_token_request.client_id = 'wgqergewrg'

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
