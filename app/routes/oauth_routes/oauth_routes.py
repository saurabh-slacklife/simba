from app import logger

from flask import Blueprint, request, redirect, Response

from app.common import Urls
from app.exception_handlers import BadRequest, BaseUserException
from app.extensions.dependency_extensions import oauth_service
from app.models.request.auth.oauth_request import GrantAuthRequest, AuthTokenRequest, RefreshTokenRequest
from app.models.response.auth_token.oauth_response import AuthTokenResponseEncoder
from app.extensions.dependency_extensions import http_client

oauth_route = Blueprint("Oauth", __name__)


@oauth_route.route('/authorize', methods=['GET'])
def authorize_client():
    req_args = request.args

    response_type = req_args.get('response_type')
    scopes = req_args.get('scopes')
    client_id = req_args.get('client_id')
    state = req_args.get('state')

    if not response_type and response_type != 'code':
        raise BadRequest(message={'message': 'Invalid response_type'})
    if not scope:
        raise BadRequest(message={'message': 'Invalid scopes'})
    if not client_id:
        raise BadRequest(message={'message': 'Invalid client_id'})
    if not state:
        raise BadRequest(message={'message': 'Invalid state'})

    auth_header = request.headers.get('Authorization')

    if not auth_header:
        raise BadRequest(message={'message': 'Authorization header'})

    user_id = get_user_id(auth_header)
    if not user_id and user_id == 0:
        return redirect(Urls.SESSION, 302)

    oauth_grant_code_request = GrantAuthRequest()
    oauth_grant_code_request.grant_type = response_type
    scopes_set = set(x for x in scopes.split(','))
    oauth_grant_code_request.scope = scopes_set
    oauth_grant_code_request.client_id = client_id
    oauth_grant_code_request.state = state

    auth_code, redirect_uri = oauth_service.create_oauth_grant_code_and_redirect_uri(
        oauth_grant_code_request=oauth_grant_code_request)

    uri = f'{redirect_uri}?code={auth_code}&state={oauth_grant_code_request.state}'

    oauth_service.bind_user_client(user_id, client_id)

    return redirect(uri, 302)


@oauth_route.route('/token', methods=['POST'])
def auth_token_request() -> Response:
    oauth_token_request = AuthTokenRequest()

    oauth_token_request.client_secret = request.form['client_secret']
    oauth_token_request.client_id = request.form['client_id']
    oauth_token_request.redirect_uri = request.form['redirect_uri']

    if not request.form['grant_type']:
        raise BadRequest(message={'message': 'Invalid Grant Type'})
    elif 'authorization_code' != request.form['grant_type'] and not request.form['code']:
        raise BadRequest(message={'message': 'Invalid Grant Type'})
    else:
        oauth_token_request.grant_type = request.form['grant_type']
        oauth_token_request.code = request.form['code']
        oauth_token_response = oauth_service.process_auth_token_request(oauth_token_request=oauth_token_request)
        return AuthTokenResponseEncoder().encode(oauth_token_response)


@oauth_route.route('/token/refresh', methods=['POST'])
def token_refresh_request() -> Response:
    if not request.form['grant_type']:
        raise BadRequest(message={'message': 'Invalid Grant Type'})
    elif 'refresh_token' != request.form['grant_type'] and not request.form['refresh_token']:
        raise BadRequest(message={'message': 'Invalid Grant Type'})
    else:
        refresh_token_request = RefreshTokenRequest(client_id=request.form['client_id'],
                                                    client_secret=request.form['client_secret'],
                                                    refresh_token=request.form['refresh_token'])
        oauth_token_response = oauth_service.process_refresh_token_request(refresh_token_request=refresh_token_request)
        return AuthTokenResponseEncoder().encode(oauth_token_response)


def get_user_id(auth_header: str):
    if auth_header:
        headers = {}
        headers.setdefault('USER-AGENT', 'SIMBA APP')
        headers.setdefault('Content-Type', 'application/json')
        headers.setdefault('Accept-Type', 'application/json')
        headers.setdefault('Authorization', auth_header)
        user_id = call_auth(headers)
        if user_id:
            return user_id
        else:
            logger.error(f'User not logged-in, redirect to Login page')
            return 0
    else:
        logger.error(f'User not logged-in, redirect to Login page')
        return 0


def call_auth(headers):
    response = http_client.get_connection.request(method='GET', url=Urls.SESSION, headers=headers)
    if response:
        response_json = response.json
        user_id = response_json.get('user_id', 'sgergewg')
        return user_id
    else:
        return 0


@oauth_route.before_request
def validate_header():
    req_content_type = request.content_type
    if not req_content_type:
        logger.error(f'Invalid Content Type: {request.content_type}')
        raise BadRequest(message={'message': 'Invalid Content Type'})
    elif (
            req_content_type == 'application/x-www-form-urlencoded;charset=utf-8'
            or req_content_type == 'application/x-www-form-urlencoded') \
            or req_content_type == 'application/json;charset=utf-8':
        pass
    else:
        logger.error(f'Invalid Content Type: {request.content_type}')
        raise BadRequest(message={'message': f'Invalid Content Type: {request.content_type}'})

    user_agent = request.headers.get('User-Agent')
    if not user_agent:
        logger.error(f'Invalid User Agent header')
        raise BadRequest(message={'message': 'Invalid User Agent header'})


@oauth_route.after_request
def add_header(response):
    response.headers['Content-Type'] = 'application/json;charset=utf-8'
    response.headers['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.encoding = 'utf-8'
    return response


@oauth_route.errorhandler(BaseUserException)
def handle_error(e: BaseUserException):
    return e.get_response()
