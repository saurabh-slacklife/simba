import logging
from datetime import datetime
from hashlib import sha256

from redis import Redis

from app.client.redis_client import RedisClient
from app.config.config import ConfigType
from app.dao.auth_token_dao import fetch_auth_code_client_info, persist_auth_code, persist_token
from app.dao.auth_token_dao import fetch_refresh_token_client_info, revoke_access_refresh_token
from app.dao.auth_token_dao import redis_get_client_info
from app.exception_handlers import OperationNotAllowedException, BadRequestException, UnAuthorized
from app.models.request.auth.oauth_request import GrantAuthRequest, AuthTokenRequest, RefreshTokenRequest
from app.models.response.auth_token.oauth_response import AuthTokenResponse
from app import logger


class OAuthService(object):
    def __init__(self, redis_client: RedisClient = None, config_object: ConfigType = None):
        self._redis_connection: Redis = None
        self._redis_client = redis_client
        self._config_object = config_object

    def init_service(self, redis_client: RedisClient, config_object: ConfigType):
        self._redis_connection = redis_client.redis_connection
        self._config_object = config_object

    def __generate_sha__(self, key: str, value: str) -> str:
        current_time = datetime.utcnow()
        hash_value = "%s:%s:%s" % (value, current_time.isoformat(), key)
        return sha256(hash_value.encode('utf-8')).hexdigest()

    # Auth Code flow

    def create_oauth_grant_code_and_redirect_uri(self, oauth_grant_code_request: GrantAuthRequest):
        return self.__get_auth_code_and_redirect_uri__(oauth_grant_code_request)

    def __get_auth_code_and_redirect_uri__(self, oauth_grant_code_request: GrantAuthRequest):
        client_id = oauth_grant_code_request.client_id
        input_scope = oauth_grant_code_request.scope

        scope_set, redirect_uri = self.__get_scope_redirect_uri__(client_id, input_scope)

        for scope in input_scope:
            if scope not in scope_set:
                logger.error(f'Invalid input scope: {input_scope} request for Client: {client_id}')
                raise OperationNotAllowedException(message='Invalid Scopes')

        oauth_code = self.__generate_sha__(client_id, scope_set)
        self.__persist_code__(code=oauth_code, client_id=client_id)
        logger.info(f'Auth_Code: {oauth_code} and redirect_uri: {redirect_uri}')
        return oauth_code, redirect_uri

    def __get_scope_redirect_uri__(self, client_id: str, scopes: str) -> set:
        response_list = redis_get_client_info(self._redis_connection, client_id, self._config_object.CLIENT_DB,
                                              'scope', 'redirect_uri')
        logger.info(f'response_list size: {len(response_list)} response: {response_list}')
        if len(response_list) == 2:
            redis_response = response_list[1]
            return set(x for x in redis_response[0].decode('utf-8').split(',')), redis_response[1].decode('utf-8')
        else:
            raise OperationNotAllowedException(message='Invalid Request')

    def __persist_code__(self, code: str, client_id: str):
        persist_auth_code(redis_connection=self._redis_connection, name=code, value=client_id, expire=600,
                          db=self._config_object.AUTH_CODE_DB)

    # Access Token Flow

    def process_auth_token_request(self, oauth_token_request: AuthTokenRequest) -> AuthTokenResponse:
        if self.__is_token_request_valid__(oauth_token_request=oauth_token_request):

            access_token, refresh_token = self.__generate_access_refresh_token__(
                client_id=oauth_token_request.client_id,
                client_secret=oauth_token_request.client_secret)

            oauth_response = AuthTokenResponse(access_token=access_token, refresh_token=refresh_token,
                                               token_type='API-Access', expires=3600)

            persist_token(redis_connection=self._redis_connection, client_id=oauth_token_request.client_id,
                          oauth_response=oauth_response, auth_code=oauth_token_request.code,
                          client_db=self._config_object.CLIENT_DB, auth_code_db=self._config_object.AUTH_CODE_DB)

            return oauth_response
        else:
            raise UnAuthorized(message='Invalid Client Id')

    def __is_token_request_valid__(self, oauth_token_request: AuthTokenRequest):
        response_list = fetch_auth_code_client_info(redis_connection=self._redis_connection,
                                                    oauth_token_request=oauth_token_request,
                                                    db_1=self._config_object.AUTH_CODE_DB,
                                                    db_2=self._config_object.CLIENT_DB)

        logger.info(f'Token Request response: {response_list} and length: {len(response_list)}')

        if len(response_list) == 4:
            if response_list[1] is None:
                raise UnAuthorized(message='Invalid Auth Code')
            else:
                persisted_client_id = response_list[1].decode('utf-8')
                client_id = oauth_token_request.client_id
                if persisted_client_id == client_id:
                    persisted_client_info = response_list[3]
                    if len(persisted_client_info) == 2:
                        persisted_client_secret = persisted_client_info[0].decode('utf-8')
                        persisted_redirect_uri = persisted_client_info[1].decode('utf-8')
                        if (oauth_token_request.redirect_uri == persisted_redirect_uri and
                                oauth_token_request.client_secret == persisted_client_secret):
                            return True
                        else:
                            raise BadRequestException(message='Invalid client information')
                    else:
                        raise BadRequestException(message='Invalid client information')
                else:
                    raise UnAuthorized(message='Invalid Auth Code or Client Id combination')
        else:
            raise UnAuthorized(message='Invalid Auth Code or Client Id combination')

    def __generate_access_refresh_token__(self, client_id: str, client_secret: str):
        token_str = "%s:%s" % (client_secret, client_id)
        refresh_str = "%s:%s" % (token_str, "refresh")

        # Step 1 Generate Refresh Token
        refresh_token = self.__generate_sha__(key='refresh', value=refresh_str)

        # Step 2 Generate Access Token
        access_token = self.__generate_sha__(key='access', value=token_str)

        return access_token, refresh_token

    # Refresh Token flow

    def process_refresh_token_request(self, refresh_token_request: RefreshTokenRequest):
        # Step 1 Validate authenticated client by id and secret
        # Step 2 Check Token in Redis
        # Step 3 Check refresh token mapping with client along with
        is_request_valid, persisted_access_token = self.__validate_refresh_token_request_(refresh_token_request)

        # Step 4 Revoke earlier OAuth Token if exists
        # Step 5 revoke the mapping between Refresh_token - OAuth_token - Client
        # Step 5 Revoke earlier Refresh Token
        if is_request_valid:
            self.__revoke_token_mappings__(refresh_token_request, persisted_access_token)

            # Step 6 Generate new Refresh token and Oauth token with same scope with which Refresh token was generated
            access_token, refresh_token = self.__generate_access_refresh_token__(
                client_id=refresh_token_request.client_id,
                client_secret=refresh_token_request.client_secret)

            oauth_response = AuthTokenResponse(access_token=access_token, refresh_token=refresh_token,
                                               token_type='API-Access', expires=3600)

            # Step 7 Persist new refresh token and oauth token, with expiry.
            persist_token(redis_connection=self._redis_connection, client_id=refresh_token_request.client_id,
                          oauth_response=oauth_response, auth_code=None,
                          client_db=self._config_object.CLIENT_DB, auth_code_db=None)

            return oauth_response

    def __validate_refresh_token_request_(self, refresh_token_request: RefreshTokenRequest):
        # Step 1 Validate authenticated client by id and secret
        # Step 2 Check Token in Redis
        # Step 3 Check refresh token mapping with client along with

        response_list = fetch_refresh_token_client_info(redis_connection=self._redis_connection,
                                                        refresh_token_request=refresh_token_request,
                                                        client_db=self._config_object.CLIENT_DB)

        if response_list and len(response_list) == 4:
            if response_list[1]:
                persisted_access_token = response_list[1].decode('utf-8')
                if response_list[2]:
                    persisted_client_info = response_list[3]
                    if len(persisted_client_info) == 2:
                        persisted_client_secret = persisted_client_info[0].decode('utf-8')
                        persisted_client_id = persisted_client_info[1].decode('utf-8')
                        if (persisted_client_id != refresh_token_request.client_id
                                and persisted_client_secret != refresh_token_request.client_secret):
                            raise BadRequestException(f'Invalid Client ID and Refresh Token Mapping')
                        else:
                            return True, persisted_access_token
                    else:
                        raise BadRequestException(f'Invalid Client ID and Refresh Token Mapping')
                else:
                    logger.error(
                        f'No mapping exists between: Client Id: {refresh_token_request.client_id}, refresh Token: {refresh_token_request.refresh_token}')
                    raise BadRequestException(f'Invalid Refresh token  ')
            else:
                logger.error(f'Refresh Token doesn\'t exists')
                raise UnAuthorized(f'Invalid Refresh token  ')
        else:
            logger.error(
                f'No mapping exists between: Client Id: {refresh_token_request.client_id}, refresh Token: {refresh_token_request.refresh_token}')
            raise UnAuthorized(f'Invalid Refresh token  ')

    def __revoke_token_mappings__(self, refresh_token_request: RefreshTokenRequest, persisted_access_token: str):
        # Step 4 Revoke earlier OAuth Token if exists
        # Step 5 revoke the mapping between Refresh_token - OAuth_token - Client
        # Step 5 Revoke earlier Refresh Token

        response_list = revoke_access_refresh_token(redis_connection=self._redis_connection,
                                                    refresh_token_request=refresh_token_request,
                                                    persisted_access_token=persisted_access_token,
                                                    client_db=self._config_object.CLIENT_DB)

        logger.info(f'=============response_list size: {len(response_list)}')

        # if not response_list and len(response_list) >= 3:
        #     if not response_list[1] and not response_list[2] and not response_list[3]:
        #         tokens_deleted =response_list[1].decode('utf-8')
