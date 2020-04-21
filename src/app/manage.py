import logging
import os
from flask import Flask

from src.app.client.redis_client import RedisClient
from src.app.config.config import ConfigType
from src.app.routes import user
from src.app.routes.oauth_routes.oauth_routes import oauth_route

from src.app.extensions.dependency_extensions import user_service, oauth_service, redis_health_service


class ManageApp(object):

    def __init__(self):
        self.service_env = os.environ.get('SERVICE_ENV')
        self.config_object = ConfigType(self.service_env)

        self._simba_app = Flask('config', template_folder=None, static_folder=None)
        self._simba_app.config.from_object(self.config_object)

        self.initialize_app()

    def initialize_app(self):
        redis_client = RedisClient(config=self._simba_app.config)
        self.__register_services__(redis_client=redis_client)

        self.__register_blueprints__()

    def __register_blueprints__(self):
        self._simba_app.register_blueprint(blueprint=user.user_bp, url_prefix='/user')
        self._simba_app.register_blueprint(blueprint=oauth_route, url_prefix='/oauth')

    def __register_services__(self, redis_client: RedisClient):
        user_service.init_service(redis_client=redis_client, config_object=self.config_object)
        oauth_service.init_service(redis_client=redis_client, config_object=self.config_object)

        from src.app.models.response.health import Health

        redis_health_service.init_service(redis_client=redis_client, health=Health())

    @property
    def logger(self):
        logger = logging.getLogger()
        return logger

    @property
    def get_simba_app(self):
        return self._simba_app
