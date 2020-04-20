from main.app.client.redis_client import RedisClient
from main.app.models.request.auth.oauth_request import OAuthGrantAuthRequest
from main.app.config.config import ConfigType

from redis import WatchError


class OAuthService(object):
    def __init__(self, redis_client=None, config_object=None):
        self._redis_client = redis_client
        self._config_object = config_object

    def init_service(self, redis_client: RedisClient, config_object: ConfigType):
        if not self._redis_client:
            self._redis_client = redis_client
        self._config_object = config_object

    def create_oauth_grant_code(self, oauth_grant_code_request: OAuthGrantAuthRequest):
        self.__client_validations__(oauth_grant_code_request)

    def __client_validations__(self, oauth_grant_code_request: OAuthGrantAuthRequest):
        client_id = oauth_grant_code_request.client_id
        scope = oauth_grant_code_request.scope

        response_list = self.__redis_hmget_query_transaction__(client_id, 'scope')


    def __redis_hmget_query_transaction__(self, name, keys):
        try:
            with self.__redis_client.pipeline() as pipe:
                pipe.execute_command('SELECT', self._config_object.CLIENT_DB)
                pipe.hmget(name, keys)
                pipe_response = pipe.execute()
                return pipe_response
        except WatchError:
            return self.__fallback_redis_hmget_query__(name, keys)

    def __fallback_redis_get_query__(self, name, keys):
        self.__redis_client.execute_command('SELECT', self._config_object.CLIENT_DB)
        response_list = self.__redis_client.hmget(name, keys)
        return response_list
