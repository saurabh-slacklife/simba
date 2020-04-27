from app import logger

from flask import Blueprint, request, redirect, Response

from app.exception_handlers import BadRequest, BaseUserException
from app.extensions.dependency_extensions import oauth_service
from app.models.request.auth.oauth_request import GrantAuthRequest, AuthTokenRequest, RefreshTokenRequest
from app.models.response.auth_token.oauth_response import AuthTokenResponseEncoder
from app.routes import logged_in

oauth_route = Blueprint("Oauth", __name__)


@oauth_route.route('/access', methods=['GET'])
def authorize_client():
    req_args = request.args

    if not req_args.get('response_type') and req_args.get('response_type') != 'code':
        raise BadRequest(message={'message': 'Invalid response_type'})
    if not req_args.get('scope'):
        raise BadRequest(message={'message': 'Invalid scope'})
    if not req_args.get('client_id'):
        raise BadRequest(message={'message': 'Invalid client_id'})
    if not req_args.get('state'):
        raise BadRequest(message={'message': 'state'})

    oauth_grant_code_request = GrantAuthRequest()
    oauth_grant_code_request.grant_type = req_args.get('response_type')
    oauth_grant_code_request.scope = set(x for x in req_args.get('scope').split(','))
    oauth_grant_code_request.client_id = req_args.get('client_id')
    oauth_grant_code_request.state = req_args.get('state')

    auth_code, redirect_uri = oauth_service.create_oauth_grant_code_and_redirect_uri(
        oauth_grant_code_request=oauth_grant_code_request)

    uri = f'{redirect_uri}?code={auth_code}&state={oauth_grant_code_request.state}'

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


@oauth_route.route('/test', methods=['GET'])
@logged_in
def authorize_check():
    return {"hello": "success"}


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
