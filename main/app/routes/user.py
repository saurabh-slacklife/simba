from flask import Blueprint

user_bp = Blueprint("User", __name__)


@user_bp.route("/", methods=['POST'])
def create_user():
    pass


@user_bp.route("/", methods=['GET'])
def get_user():
    return "Hello User"
