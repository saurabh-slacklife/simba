import os
from flask import Flask

from app.client.redis_client import RedisClient
from app.client.elasticsearch_client import ElasticSearchClient
from app.config.config import ConfigType
from app.routes.user import user_bp
from app.routes.oauth_routes.oauth_routes import oauth_route
from app.routes.client_route import client_route

from app.extensions.dependency_extensions import user_service, oauth_service, redis_health_service, client_service


class ManageApp(object):

    def __init__(self):
        self.service_env = os.environ.get('SERVICE_ENV')
        self.config_object = ConfigType(self.service_env)

        self._simba_app = Flask('config', template_folder=None, static_folder=None)
        self._simba_app.config.from_object(self.config_object)
        self.initialize_app()

    def initialize_app(self):
        redis_client = RedisClient(config=self._simba_app.config)
        elastic_client = ElasticSearchClient(config=self._simba_app.config)
        self.__register_services__(redis_client=redis_client, elastic_client=elastic_client)

        self.__register_blueprints__()

    def __register_blueprints__(self):
        self._simba_app.register_blueprint(blueprint=user_bp, url_prefix='/user')
        self._simba_app.register_blueprint(blueprint=oauth_route, url_prefix='/oauth')
        self._simba_app.register_blueprint(blueprint=client_route, url_prefix='/client')

    def __register_services__(self, redis_client: RedisClient, elastic_client: ElasticSearchClient):
        user_service.init_service(redis_client=redis_client, config_object=self.config_object)
        oauth_service.init_service(redis_client=redis_client, config_object=self.config_object)
        client_service.init_service(redis_client=redis_client, elastic_client=elastic_client,
                                    config_object=self.config_object)

        from app.models.response.health import Health

        redis_health_service.init_service(redis_client=redis_client, health=Health())

    @property
    def get_simba_app(self):
        return self._simba_app


manage_app = ManageApp()
simba_flask_app = manage_app.get_simba_app


@simba_flask_app.errorhandler(500)
def handle_500(error):
    return "It's Okay! Life is funny at times"
