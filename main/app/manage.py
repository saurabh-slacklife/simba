import logging
import os

from flask import Flask

from main.app.config.Config import ConfigType
from main.app.routes import user


def create_app() -> Flask:
    logger = logging.getLogger()
    flask_app = Flask('app', template_folder=None, static_folder=None)
    service_env = os.environ.get('SERVICE_ENV')
    flask_app.config.from_object(ConfigType(service_env))
    __register_blueprints__(flask_app)
    return flask_app


def __register_blueprints__(flask_app: Flask):
    flask_app.register_blueprint(user.user_bp)
