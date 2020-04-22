import logging
from datetime import datetime
from hashlib import sha256

from redis import Redis

from src.app.client.redis_client import RedisClient
from src.app.config.config import ConfigType
from src.app.dao.auth_token_dao import fetch_auth_code_client_info, persist_auth_code, persist_token
from src.app.dao.auth_token_dao import redis_get_client_info
from src.app.exception_handlers import OperationNotAllowedException, BadRequestException
from src.app.models.request.auth.oauth_request import GrantAuthRequest, AuthTokenRequest
from src.app.models.response.auth_token.oauth_response import AuthTokenResponse

logger = logging.getLogger('gunicorn.error')


class OAuthService(object):
    def __init__(self, redis_client: RedisClient = None, config_object: ConfigType = None):
        self._redis_connection: Redis = None
        self._redis_client = redis_client
        self._config_object = config_object

    def init_service(self, redis_client: RedisClient, config_object: ConfigType):
        self._redis_connection = redis_client.redis_connection
        self._config_object = config_object

    def __generate_sha__(self, client_id: str, value: str) -> str:
        current_time = datetime.utcnow()
        hash_value = "%s:%s:%s" % (value, current_time.isoformat(), client_id)
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
        return oauth_code, redirect_uri

    def __get_scope_redirect_uri__(self, client_id: str, scopes: str) -> set:
        response_list = redis_get_client_info(self._redis_connection, client_id, self._config_object.CLIENT_DB,
                                              'scope', 'redirect_uri')
        logger.error(f'response_list size: {len(response_list)} response: {response_list}')
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

            access_token, refresh_token = self.__generate_access_token__(oauth_token_request=oauth_token_request)

            oauth_response = AuthTokenResponse(access_token=access_token, refresh_token=refresh_token,
                                               token_type='API-Access', expires=3600)

            persist_token(redis_connection=self._redis_connection, client_id=oauth_token_request.client_id,
                          oauth_response=oauth_response, auth_code=oauth_token_request.code,
                          client_db=self._config_object.CLIENT_DB, auth_code_db=self._config_object.AUTH_CODE_DB)

            return oauth_response
        else:
            raise BadRequestException(message='Invalid Client Id')

    def __is_token_request_valid__(self, oauth_token_request: AuthTokenRequest):
        client_id = oauth_token_request.client_id
        response_list = fetch_auth_code_client_info(redis_connection=self._redis_connection,
                                                    oauth_token_request=oauth_token_request,
                                                    db_1=self._config_object.AUTH_CODE_DB,
                                                    db_2=self._config_object.CLIENT_DB)

        logger.info(f'Token Request response: {response_list} and length: {len(response_list)}')

        if len(response_list) == 4:
            persisted_client_id = response_list[1].decode('utf-8')
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
                raise BadRequestException(message='Invalid Auth Code or Client Id combination')
        else:
            raise BadRequestException(message='Invalid Auth Code or Client Id combination')

    def __generate_access_token__(self, oauth_token_request):
        token_str = "%s:%s" % (oauth_token_request.grant_type, oauth_token_request.grant_type)
        # Step 1 Generate Refresh Token
        access_token = self.__generate_sha__(client_id=oauth_token_request.client_id, value=token_str)
        refresh_str = "%s:%s" % (token_str, "refresh")
        # Step 2 Generate Access Token
        refresh_token = self.__generate_sha__(client_id=oauth_token_request.client_id, value=refresh_str)
        return access_token, refresh_token
