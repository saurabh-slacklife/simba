from functools import wraps
from flask import request, redirect
from app import logger
from app.common import Urls
from app.extensions.dependency_extensions import http_client


def logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        header = request.headers.get('Authorization')
        req_args = request.args
        logger.info(f'Request args: {req_args}')
        if header:

            headers = {}
            headers.setdefault('USER-AGENT', 'SIMBA APP')
            headers.setdefault('Content-Type', 'application/json')
            headers.setdefault('Accept-Type', 'application/json')

            http_client.get_connection.request(method='GET',url=Urls.SESSION)
            logger.info(f'Valid Auth Request: {header}')

            return f(*args, **kwargs)
        else:
            logger.error(f'User not logged in redirecting to Login page')
            # return redirect(Urls.SESSION)
            return f(*args, **kwargs)

    return decorated_function
