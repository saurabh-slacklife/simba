from flask import Blueprint, request, Response
# from app import logger
from app.extensions.dependency_extensions import client_service as cs
from app.elastic_entities.client import ClientEntity
from app.exception_handlers import BadRequestException, BaseUserException

import logging

logger = logging.getLogger('gunicorn.error')

client_route = Blueprint("Client", __name__)


@client_route.route('/', methods=['PUT'])
def register_client() -> Response:
    client_entity = validate_request(rq=request)

    doc_status, doc_meta = cs.create_client(client_entity)

    return request.form.get('client_name', default='something')


def validate_request(rq: request):
    invalid_request_dict = {}
    if not request.form['client_name']:
        invalid_request_dict['client_name'] = rq.form['client_name']
    if not request.form['email']:
        invalid_request_dict['email'] = rq.form['email']
    if not request.form['web_url']:
        invalid_request_dict['web_url'] = rq.form['web_url']
    if not request.form['contact_number']:
        invalid_request_dict['contact_number'] = rq.form['contact_form']

    if len(invalid_request_dict.items()) > 0:
        logger.error(f'Invalid request: {invalid_request_dict}')
        raise BadRequestException(message=f'Invalid request: {invalid_request_dict}')

    client_entity = ClientEntity(client_name=rq.form['client_name'], email=rq.form['email'],
                                 website=rq.form['web_url'], contact_number=rq.form['contact_number'],
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
