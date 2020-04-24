from flask import Blueprint

client_route = Blueprint("Client", __name__)


@client_route.route('/', methods=['PUT'])
def register_client():
    return 'register'


@client_route.route('/', methods=['GET'])
def client_info():
    return 'info'


@client_route.route('/', methods=['POST'])
def client_update():
    return 'update'
