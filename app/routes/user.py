from flask import Blueprint

from app.extensions.dependency_extensions import user_service

user_bp = Blueprint("User", __name__)


@user_bp.route("/", methods=['POST'])
def create_user():
    pass


@user_bp.route("/", methods=['GET'])
def get_user():
    return user_service.read()
