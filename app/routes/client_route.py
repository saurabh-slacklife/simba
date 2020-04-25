from flask import Blueprint, request, Response, json
# from app import logger
from app.extensions.dependency_extensions import client_service as cs
from app.elastic_entities.client import ClientEntity
from app.exception_handlers import BadRequestException, BaseUserException

import logging

logger = logging.getLogger('gunicorn.error')

client_route = Blueprint("Client", __name__)


@client_route.route('/', methods=['PUT'])
def register_client() -> Response:
    req_data = request.json

    client_entity = __validate_request__(req_data)

    doc_status, doc_meta = cs.create_client(client_entity)

    return {'status': doc_status,
            'id': doc_meta.id}


def __validate_request__(req_data):
    invalid_request_dict = {}
    if req_data.get('client_name') is None:
        invalid_request_dict['client_name'] = None
    if req_data.get('email') is None:
        invalid_request_dict['email'] = None
    if req_data.get('website') is None:
        invalid_request_dict['web_url'] = None
    if req_data.get('contact_number') is None:
        invalid_request_dict['contact_number'] = None

    if len(invalid_request_dict.items()) > 0:
        logger.error(f'Invalid request: {invalid_request_dict}')
        raise BadRequestException(message=f'Invalid request: {invalid_request_dict}')

    client_entity = ClientEntity(client_name=req_data.get('client_name'), email=req_data.get('email'),
                                 website=req_data.get('website'), contact_number=req_data.get('contact_number'),
                                 )
    return client_entity


@client_route.route('/', methods=['GET'])
def client_info():
    return 'info'


@client_route.route('/', methods=['POST'])
def client_update():
    return 'update'


@client_route.after_request
def add_header(response):
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    response.headers['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.encoding = 'utf-8'
    return response


@client_route.errorhandler(BaseUserException)
def handle_error(e: BaseUserException):
    logger.error(f'Error: {e.get_response()}', exc_info=True)
    return e.get_response()
