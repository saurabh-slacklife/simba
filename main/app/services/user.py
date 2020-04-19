from main.app.client.redis_client import RedisClient


class UserService(object):
    def __init__(self, redis_client=None):
        self._redis_client = redis_client

    def init_service(self, redis_client: RedisClient):
        if not self._redis_client:
            self._redis_client = redis_client

    def create_user(self, user: str):
        connection = self._redis_client.redis_connection
        connection.set(name=user, value=user)

    def read(self):
        return 'All Good'
