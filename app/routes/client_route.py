import logging

from flask import Blueprint, request, redirect, Response

from app.exception_handlers import BadRequestException, BaseUserException

client_bp = Blueprint("Client", __name__)
