from src.app.client.redis_client import RedisClient
from src.app.config.config import ConfigType


class UserService(object):
    def __init__(self, redis_client=None, config_object=None):
        self._redis_client = redis_client

    def init_service(self, redis_client: RedisClient, config_object: ConfigType):
        if not self._redis_client:
            self._redis_client = redis_client
            self._config_object = config_object

    def create_user(self, user: str):
        connection = self._redis_client.redis_connection
        connection.set(name=user, value=user)

    def read(self):
        return 'All Good'
