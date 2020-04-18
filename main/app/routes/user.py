from flask import Blueprint

user_bp = Blueprint("User", __name__)


class UserRoute:
    @staticmethod
    @user_bp.route("/", methods=['POST'])
    def create_user():
        pass

    @staticmethod
    @user_bp.route("/", methods=['GET'])
    def get_user():
        return "Hello User"
