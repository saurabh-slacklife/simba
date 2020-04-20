from flask import Blueprint, request, jsonify

from main.app.extensions.dependency_extensions import oauth_service
from main.app.models.request.auth.oauth_request import OAuthGrantAuthRequest

from main.app.exception_handlers import BadRequestException

oauth_route = Blueprint("Oauth", __name__)


@oauth_route.route('/access', methods=['GET'])
def authorize_client():
    req_args = request.args

    if not req_args.get('response_type'):
        raise BadRequestException(message={'message': 'Invalid response_type'}, error_code=400)
    if not req_args.get('scope'):
        raise BadRequestException(message={'message': 'Invalid scope'}, error_code=400)
    if not req_args.get('client_id'):
        raise BadRequestException(message={'message': 'Invalid client_id'}, error_code=400)
    if not req_args.get('state'):
        raise BadRequestException(message={'message': 'state'}, error_code=400)

    oauth_grant_code_request = OAuthGrantAuthRequest()
    oauth_grant_code_request.response_type = req_args.get('response_type')
    oauth_grant_code_request.scope = req_args.get('scope')
    oauth_grant_code_request.client_id = req_args.get('client_id')
    oauth_grant_code_request.state = req_args.get('state')

    oauth_service.create_oauth_grant_code(oauth_grant_code_request=oauth_grant_code_request)

    auth_response = jsonify('resp_dict')
    auth_response.status_code = 200

    return auth_response


@oauth_route.before_request
def validate_header():
    req_headers = request.headers
    req_content_type = req_headers.get(key='Content-Type')
    req_accept_type = req_headers.get(key='Accept-Type')
    if not req_content_type:
        raise BadRequestException(message={'message': 'Invalid Content Type'}, error_code=400)
    elif req_content_type != 'application/x-www-form-urlencoded':
        raise BadRequestException(message={'message': 'Invalid Content Type'}, error_code=400)

    if not req_accept_type:
        raise BadRequestException(message={'message': 'Invalid Accept Type'}, error_code=400)
    elif req_accept_type != 'application/json':
        raise BadRequestException(message={'message': 'Invalid Accept Type'}, error_code=400)


@oauth_route.after_request
def add_header(response):
    response.headers['Content-Type'] = 'application/json'
    response.headers['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


@oauth_route.errorhandler(BadRequestException)
def handle_error(e: BadRequestException):
    return e.get_response()
