from datetime import datetime
from hashlib import md5

from app import logger
from app.client.elasticsearch_client import ElasticSearchClient
from app.client.redis_client import RedisClient
from app.config.config import ConfigType
from app.dao.auth_token_dao import fetch_auth_code_client_info, persist_auth_code, persist_token, redis_sadd_pipeline
from app.dao.auth_token_dao import fetch_refresh_token_client_info, revoke_access_refresh_token
from app.dao.es_client_dao_impl import EsClientDaoImp
from app.dao.user_dao import UserDaoImp
from app.exception_handlers import RequestForbidden, BadRequest, UnAuthorized
from app.models.request.auth.oauth_request import GrantAuthRequest, AuthTokenRequest, RefreshTokenRequest
from app.models.response.auth_token.oauth_response import AuthTokenResponse


class OAuthService(object):
    def __init__(self, redis_client: RedisClient = None,
                 config_object: ConfigType = None):
        self._redis_connection = redis_client
        self._redis_client = redis_client
        self._config_object = config_object
        self.client_dao = None
        self.user_dao = None

    def init_service(self, redis_client: RedisClient,
                     elastic_client: ElasticSearchClient,
                     config_object: ConfigType):
        self._redis_connection = redis_client.redis_connection
        self._config_object = config_object
        self.client_dao = EsClientDaoImp(elastic_client.elastic_connection)
        self.user_dao = UserDaoImp(elastic_client.elastic_connection)

    def __generate_hash__(self, key: str, value: str) -> str:
        current_time = datetime.utcnow()
        hash_value = "%s:%s:%s" % (value, current_time.isoformat(), key)
        return md5(hash_value.encode('utf-8')).hexdigest()

    # Auth Code flow

    def validate_scopes(self, client_id: str, request_scope: set):
        client_response = self.client_dao.search_by_id(client_id=client_id)
        if not client_response:
            raise RequestForbidden(message='Invalid Client Id')
        else:
            persisted_scope = set(scope for scope in client_response.get('scopes'))
            is_req_scope_present = request_scope.difference(persisted_scope)

            if is_req_scope_present:
                raise BadRequest(message=f'Invalid request Scope: {request_scope}')

    def create_oauth_grant_code_and_redirect_uri(self, oauth_grant_code_request: GrantAuthRequest):
        return self._get_auth_code_and_redirect_uri(oauth_grant_code_request)

    def _get_auth_code_and_redirect_uri(self, oauth_grant_code_request: GrantAuthRequest):
        client_id = oauth_grant_code_request.client_id
        input_scopes = oauth_grant_code_request.scope

        self.validate_scopes(client_id=client_id, request_scope=input_scopes)

        redirect_uri = self._get_redirect_uri(client_id, input_scopes)

        oauth_code = self.__generate_hash__(client_id, '-'.join(input_scopes))
        self._persist_code(code=oauth_code, client_id=client_id)
        logger.info(f'Auth_Code: {oauth_code} and redirect_uri: {redirect_uri}')
        return oauth_code, redirect_uri

    def _get_redirect_uri(self, client_id: str, request_scope: str) -> set:

        client_response = self.client_dao.search_by_id(client_id=client_id)
        persisted_scope = set(scope for scope in client_response.get('scopes'))
        is_req_scope_present = request_scope.difference(persisted_scope)

        if is_req_scope_present:
            raise BadRequest(message=f'Invalid request Scope: {request_scope}')
        return client_response.get('redirect_url')

    def _persist_code(self, code: str, client_id: str):
        persist_auth_code(redis_connection=self._redis_connection, name=code, value=client_id, expire=600,
                          db=self._config_object.AUTH_CODE_DB)

    def bind_user_client(self, user_id: str, client_id: str):
        redis_sadd_pipeline(user_id, self._config_object.USER_DB, client_id)

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
                            raise BadRequest(message='Invalid client information')
                    else:
                        raise BadRequest(message='Invalid client information')
                else:
                    raise UnAuthorized(message='Invalid Auth Code or Client Id combination')
        else:
            raise UnAuthorized(message='Invalid Auth Code or Client Id combination')

    def __generate_access_refresh_token__(self, client_id: str, client_secret: str):
        token_str = "%s:%s" % (client_secret, client_id)
        refresh_str = "%s:%s" % (token_str, "refresh")

        # Step 1 Generate Refresh Token
        refresh_token = self.__generate_hash__(key='refresh', value=refresh_str)

        # Step 2 Generate Access Token
        access_token = self.__generate_hash__(key='access', value=token_str)

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
                            raise BadRequest(f'Invalid Client ID and Refresh Token Mapping')
                        else:
                            return True, persisted_access_token
                    else:
                        raise BadRequest(f'Invalid Client ID and Refresh Token Mapping')
                else:
                    logger.error(
                        f'No mapping exists between: Client Id: {refresh_token_request.client_id}, refresh Token: {refresh_token_request.refresh_token}')
                    raise BadRequest(f'Invalid Refresh token  ')
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
