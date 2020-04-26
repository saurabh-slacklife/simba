from flask import Blueprint, request, Response, jsonify
from app import logger
from app.extensions.dependency_extensions import client_service as cs
from app.elastic_entities.client import ClientEntity
from app.exception_handlers import BadRequest, BaseUserException, ResourceNotFound
from app.models.response.openapi_response import OpenApiResponse, OpenApiResponseEncoder

client_route = Blueprint("Client", __name__)


@client_route.route('/', methods=['PUT'])
def register_client() -> Response:
    req_data = request.json

    client_entity = __validate_document_request__(req_data)

    doc_status, doc_meta = cs.register(client_entity)

    if doc_status == 'created' and doc_meta.id is not None:
        uri = f"/client/?email={req_data.get('email')}"
        resp = OpenApiResponse(rel='Client APP', uri=uri, action='GET', types='application/json')
        return OpenApiResponseEncoder().encode(resp)
    else:
        return Response(doc_status)


@client_route.route('/', methods=['GET'])
def find_client() -> Response:
    req_args = request.args
    email = req_args.get('email')
    contact_number = req_args.get('contact_number')

    logger.info(f'Request Contact_number: {contact_number} and type: {type(contact_number)}')
    logger.info(f'Request email: {email} and type: {type(email)}')

    if not email and not contact_number:
        raise BadRequest(message={'ErrorMessage': 'Invalid query parameters.'})

    response = cs.search(email=email, contact_number=contact_number)
    if response == 0:
        raise ResourceNotFound(message={'ErrorMessage': 'Not found with provided query parameters.'})
    else:
        return jsonify(response)


@client_route.route('/', methods=['POST'])
def update_client() -> Response:
    return 'update'


def __validate_document_request__(req_data):
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
        raise BadRequest(message=f'''{'ErrorMessage': 'Invalid request {invalid_request_dict}'}''')

    client_entity = ClientEntity(client_name=req_data.get('client_name'), email=req_data.get('email'),
                                 website=req_data.get('website'), contact_number=req_data.get('contact_number'),
                                 )
    return client_entity


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
