from flask import Blueprint, request, jsonify, Response

oauth_route = Blueprint("Oauth", __name__)


@oauth_route.route('/access', methods=['GET'])
def authorize_client():
    req_headers = request.headers
    req_content_type = req_headers.get(key='Content-Type', default='None')

    req_args = request.args

    response_type = req_args.get('response_type')
    scope = req_args.get('scope')
    client_id = req_args.get('client_id')
    state = req_args.get('state')

    resp_dict = {'client_id': client_id,
                 'scope': scope,
                 'client_id': client_id,
                 'state': state,
                 'response_type': response_type}

    auth_response = jsonify(resp_dict)
    auth_response.status_code = 200

    return auth_response


@oauth_route.url_defaults
def something():
    pass


@oauth_route.after_request
def add_header(response):
    response.headers['Content-Type'] = 'application/json'
    response.headers['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response
