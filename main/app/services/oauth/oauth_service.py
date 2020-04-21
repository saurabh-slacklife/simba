from typing import List
from redis import WatchError
from hashlib import sha256
from datetime import datetime
from main.app.client.redis_client import RedisClient
from main.app.models.request.auth.oauth_request import OAuthGrantAuthRequest
from main.app.config.config import ConfigType
from main.app.exception_handlers import OperationNotAllowedException

import logging

logger = logging.getLogger('gunicorn.error')


class OAuthService(object):
    def __init__(self, redis_client: RedisClient = None, config_object: ConfigType = None):
        self._redis_client = redis_client
        self._config_object = config_object

    def init_service(self, redis_client: RedisClient, config_object: ConfigType):
        if not self._redis_client:
            self._redis_client = redis_client
        self._config_object = config_object

    def create_oauth_grant_code_and_redirect_uri(self, oauth_grant_code_request: OAuthGrantAuthRequest):
        return self.__get_auth_code_and_redirect_uri__(oauth_grant_code_request)

    def __get_auth_code_and_redirect_uri__(self, oauth_grant_code_request: OAuthGrantAuthRequest):
        client_id = oauth_grant_code_request.client_id
        input_scope = oauth_grant_code_request.scope

        scope_set, redirect_uri = self.__get_scope_redirect_uri__(client_id, input_scope)

        logger.info(f'Redis Scope: {scope_set} and redirect_uri: {redirect_uri}')

        for scope in input_scope:
            if scope not in scope_set:
                logger.error(f'Invalid input scope: {input_scope} request for Client: {client_id}')
                raise OperationNotAllowedException(message='Invalid Scopes')
        return self.__generate_auth_code__(client_id, scope_set), redirect_uri

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

    def __redis_hmget_query_transaction__(self, name, *keys) -> List:
        with self._redis_client.redis_connection.pipeline() as pipe:
            try:
                pipe.execute_command('SELECT', self._config_object.CLIENT_DB)
                pipe.hmget(name, *keys)
                pipe_response = pipe.execute()
                return pipe_response
            except WatchError:
                return self.__fallback_redis_hmget_query__(name, keys)

    def __fallback_redis_get_query__(self, name, keys):
        self.__redis_client.execute_command('SELECT', self._config_object.CLIENT_DB)
        response_list = self.__redis_client.hmget(name, keys)
        return response_list
