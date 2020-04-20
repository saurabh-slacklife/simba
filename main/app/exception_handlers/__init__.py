from flask import Response, jsonify


class BadRequestException(Exception):
    def __init__(self, message, error_code):
        self.message = message
        self.error_code = error_code

    def get_response(self) -> Response:
        response = jsonify(self.message)
        response.status_code = self.error_code
        response.headers['Content-Type'] = 'application/json'
        return response


class InvalidRequest(Exception):
    def __init__(self, message, error_code):
        self.message = message
        self.error_code = error_code

    def get_response(self) -> Response:
        response = jsonify(self.message)
        response.status_code = self.error_code
        response.headers['Content-Type'] = 'application/json'
        return response
