from typing import List
from redis import WatchError
from hashlib import sha256
from datetime import datetime
from main.app.client.redis_client import RedisClient
from main.app.models.request.auth.oauth_request import OAuthGrantAuthRequest, OAuthTokenRequest
from main.app.config.config import ConfigType
from main.app.exception_handlers import OperationNotAllowedException

import logging

logger = logging.getLogger('gunicorn.error')


class OAuthService(object):
    def __init__(self, redis_client: RedisClient = None, config_object: ConfigType = None):
        self._redis_connection = None
        self._redis_client = redis_client
        self._config_object = config_object

    def init_service(self, redis_client: RedisClient, config_object: ConfigType):
        self._redis_connection = redis_client.redis_connection
        self._config_object = config_object

    def create_oauth_grant_code_and_redirect_uri(self, oauth_grant_code_request: OAuthGrantAuthRequest):
        return self.__get_auth_code_and_redirect_uri__(oauth_grant_code_request)

    def create_auth_token(self, oauth_token_request: OAuthTokenRequest):
        client_id = oauth_token_request.client_id
        redirect_uri = oauth_token_request.redirect_uri
        code = oauth_token_request.code
        client_secret = oauth_token_request.client_secret

        # TODO Implement this method. Compare code-to-client_id mapping and return the client_id
        self.is_auth_code_valid(code, client_id)

        #TODO Implement this method. Validate the client_secret, redirect_uri with DB
        self.is_client_valid(client_id, client_secret, redirect_uri)


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
        response_list = self.__redis_hmget_query_transaction__(client_id, 'scope', 'redirect_uri')
        logger.error(f'response_list size: {len(response_list)} response: {response_list}')
        if len(response_list) == 2:
            redis_response = response_list[1]
            return set(x for x in redis_response[0].decode('utf-8').split(',')), redis_response[1].decode('utf-8')
        else:
            raise OperationNotAllowedException(message='Invalid Request')

    # TODO Add all below Redis methods to DAO

    def __persist_code__(self, code: str, client_id: str):
        self.__redis_set_query_transaction__(name=code, value=client_id, expire=36000)

    def __redis_hmget_query_transaction__(self, name, *keys) -> List:
        with self._redis_connection.pipeline() as pipe:
            try:
                pipe.execute_command('SELECT', self._config_object.CLIENT_DB)
                pipe.hmget(name, *keys)
                pipe_response = pipe.execute()
                return pipe_response
            except WatchError:
                return self.__fallback_redis_hget_query__(name, *keys)

    def __fallback_redis_hget_query__(self, name, *keys):
        self._redis_connection.execute_command('SELECT', self._config_object.CLIENT_DB)
        response_list = self._redis_connection.hmget(name, *keys)
        return response_list

    def __redis_set_query_transaction__(self, name: str, value: str, expire: int) -> List:
        with self._redis_connection.pipeline() as pipe:
            try:
                pipe.execute_command('SELECT', self._config_object.AUTH_CODE_DB)
                pipe.set(name=name, value=value, ex=expire)
                pipe_response = pipe.execute()
                return pipe_response
            except WatchError:
                return self.__fallback_redis_set_query__(name=name, value=value, expire=expire)

    def __fallback_redis_set_query__(self, name: str, value: str, expire: int):
        self._redis_connection.execute_command('SELECT', self._config_object.AUTH_CODE_DB)
        response_list = self._redis_connection.set(name=name, value=value, ex=expire)
        return response_list
