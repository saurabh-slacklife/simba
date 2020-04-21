from typing import List
from redis import WatchError, Redis
from hashlib import sha256
from datetime import datetime
from main.app.client.redis_client import RedisClient
from main.app.models.request.auth.oauth_request import OAuthGrantAuthRequest, OAuthTokenRequest
from main.app.config.config import ConfigType
from main.app.exception_handlers import OperationNotAllowedException, BadRequestException

import logging

logger = logging.getLogger('gunicorn.error')


class OAuthService(object):
    def __init__(self, redis_client: RedisClient = None, config_object: ConfigType = None):
        self._redis_connection: Redis = None
        self._redis_client = redis_client
        self._config_object = config_object

    def init_service(self, redis_client: RedisClient, config_object: ConfigType):
        self._redis_connection = redis_client.redis_connection
        self._config_object = config_object

    def create_oauth_grant_code_and_redirect_uri(self, oauth_grant_code_request: OAuthGrantAuthRequest):
        return self.__get_auth_code_and_redirect_uri__(oauth_grant_code_request)

    def create_auth_token(self, oauth_token_request: OAuthTokenRequest):
        if self.__is_token_request_valid__(oauth_token_request=oauth_token_request):
            return self.__generate_token__(oauth_token_request=oauth_token_request)
        else:
            raise BadRequestException(message='Invalid Client Id')

    # Auth Code flow

    def __get_auth_code_and_redirect_uri__(self, oauth_grant_code_request: OAuthGrantAuthRequest):
        client_id = oauth_grant_code_request.client_id
        input_scope = oauth_grant_code_request.scope

        scope_set, redirect_uri = self.__get_scope_redirect_uri__(client_id, input_scope)

        for scope in input_scope:
            if scope not in scope_set:
                logger.error(f'Invalid input scope: {input_scope} request for Client: {client_id}')
                raise OperationNotAllowedException(message='Invalid Scopes')

        oauth_code = self.__generate_auth_code__(client_id, scope_set)
        self.__persist_code__(code=oauth_code, client_id=client_id)
        return oauth_code, redirect_uri

    def __generate_auth_code__(self, client_id: str, scopes: set) -> str:
        current_time = datetime.utcnow()
        hash_value = "%s:%s:%s" % (scopes, current_time.isoformat(), client_id)
        return sha256(hash_value.encode('utf-8')).hexdigest()

    def __get_scope_redirect_uri__(self, client_id: str, scopes: str) -> set:
        response_list = self.__redis_hmget_query_pipeline__(client_id, self._config_object.CLIENT_DB,
                                                            'scope', 'redirect_uri')
        logger.error(f'response_list size: {len(response_list)} response: {response_list}')
        if len(response_list) == 2:
            redis_response = response_list[1]
            return set(x for x in redis_response[0].decode('utf-8').split(',')), redis_response[1].decode('utf-8')
        else:
            raise OperationNotAllowedException(message='Invalid Request')

    def __persist_code__(self, code: str, client_id: str):
        self.__redis_set_query_pipeline__(name=code, value=client_id, expire=36000, db=self._config_object.AUTH_CODE_DB)

    # Access Token Flow
    def __is_token_request_valid__(self, oauth_token_request: OAuthTokenRequest):
        client_id = oauth_token_request.client_id
        response_list = self.__redis_fetch_code_client_details__(oauth_token_request=oauth_token_request,
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

    def __generate_token__(self, oauth_token_request):
        pass

    # TODO Add all below Redis methods to DAO

    def __redis_hmget_query_pipeline__(self, name, db: int, *keys) -> List:
        with self._redis_connection.pipeline() as pipe:
            try:
                pipe.execute_command('SELECT', db)
                pipe.hmget(name, *keys)
                pipe_response = pipe.execute()
                return pipe_response
            except WatchError:
                return self.__fallback_redis_hget_query__(name=name, db=db, *keys)

    def __fallback_redis_hget_query__(self, name, db: int, *keys):
        with self._redis_connection as redis_conn:
            redis_conn.execute_command('SELECT', db)
            return redis_conn.hmget(name, *keys)

    def __redis_fetch_code_client_details__(self, oauth_token_request: OAuthTokenRequest,
                                            db_1: int,
                                            db_2: int):
        with self._redis_connection.pipeline() as pipe:
            try:
                pipe.execute_command('SELECT', db_1)
                pipe.get(oauth_token_request.code)
                pipe.execute_command('SELECT', db_2)
                pipe.hmget(oauth_token_request.client_id, 'client_secret',
                           'redirect_uri')
                return pipe.execute()
            except WatchError:
                pass
        # TODO Handle fall back
        # return self.__fallback_redis_get_query__(key=key, db=db)

    def __fallback_redis_get_query__(self, key: str, db: int):
        with self._redis_connection as redis_conn:
            redis_conn.execute_command('SELECT', db)
            return redis_conn.get(key)

    def __redis_set_query_pipeline__(self, name: str, value: str, expire: int, db: int) -> List:
        with self._redis_connection.pipeline() as pipe:
            try:
                pipe.execute_command('SELECT', db)
                pipe.set(name=name, value=value, ex=expire)
                pipe_response = pipe.execute()
                return pipe_response
            except WatchError:
                return self.__fallback_redis_set_query__(name=name, value=value, expire=expire, db=db)

    def __fallback_redis_set_query__(self, name: str, value: str, expire: int, db: int):
        with self._redis_connection as redis_conn:
            redis_conn.execute_command('SELECT', db)
            return redis_conn.set(name=name, value=value, ex=expire)
