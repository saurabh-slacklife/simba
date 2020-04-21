# Author: Saurabh Saxena

from redis import Redis, RedisError

from src.app.models.response.health import Health


class RedisHealthService:
    def __init__(self, redis_client=None, health=None):
        self._redis_client = redis_client
        self._redis_health = health

    def init_service(self, redis_client: Redis, health: Health):
        self._redis_client = redis_client
        self._redis_health = health

    # Functions used for Health Check

    def check_connection_ping(self):
        return self._redis_client.ping()

    def check_connection_info(self):
        return self._redis_client.info(section='clients')

    def check_info(self):
        return self._redis_client.info()

    @property
    def redis_health(self) -> Health:
        try:
            ping_status = self._redis_client.ping()
            stats = self._redis_client.info("Stats")
            self._redis_health.health_status = {"ping_status": ping_status, "stats": stats}
            self._redis_health.health_header = "True"
            return self._redis_health
        except RedisError as e:
            self._redis_health.health_status = {"Status": 503, "Message": "System Unavailable"}
            self._redis_health.health_header = "False"
            return self._redis_health

    @redis_health.setter
    def cant_set_me(self, value=None):
        pass
