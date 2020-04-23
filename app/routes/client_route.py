import logging

from flask import Blueprint, request, redirect, Response
from app.extensions.dependency_extensions import client_service

from app.exception_handlers import BadRequestException, BaseUserException

client_route = Blueprint("Client", __name__)


@client_route.route('/', methods=['PUT'])
def register_client():
    pass


@client_route.route('/', method=['GET'])
def client_info():
    pass


@client_route.route('/', methods=['POST'])
def client_update():
    pass
