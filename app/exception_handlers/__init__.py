from flask import Response, jsonify


class BaseUserException(Exception):
    def __init__(self, message, http_status_code: int, headers=None):
        self._message = message
        self._http_status_code = http_status_code
        self._headers = headers

    def get_response(self) -> Response:
        response = jsonify(self._message)
        response.status_code = self._http_status_code
        response.headers['Content-Type'] = 'application/json'
        return response


class BadRequest(BaseUserException):
    def __init__(self, message, headers=None):
        super(BadRequest, self).__init__(message, 400, headers)


class RequestConflict(BaseUserException):
    def __init__(self, message, headers=None):
        super(RequestConflict, self).__init__(message, 409, headers)


class UnAuthorized(BaseUserException):
    def __init__(self, message: str, headers=None):
        super(UnAuthorized, self).__init__(message, 401, headers)


class InvalidRequest(BaseUserException):
    def __init__(self, message, headers=None):
        super(InvalidRequest, self).__init__(message, 400, headers)


class RequestForbidden(BaseUserException):
    def __init__(self, message, headers=None):
        super(RequestForbidden, self).__init__(message, 403, headers)


class ResourceNotFound(BaseUserException):
    def __init__(self, message, headers=None):
        super(ResourceNotFound, self).__init__(message, 404, headers)
