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


class BadRequestException(BaseUserException):
    def __init__(self, message, headers=None):
        super(BadRequestException, self).__init__(message, 400, headers)


class InvalidRequest(BaseUserException):
    def __init__(self, message, headers=None):
        super(InvalidRequest, self).__init__(message, 400, headers)


class OperationNotAllowedException(BaseUserException):
    def __init__(self, message, headers=None):
        super(OperationNotAllowedException, self).__init__(message, 403, headers)
