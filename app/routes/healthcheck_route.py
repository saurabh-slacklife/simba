from flask import Blueprint, Response, jsonify
from app.extensions.dependency_extensions import redis_health_service

redis_health_route = Blueprint('RedisHealth', __name__)


@redis_health_route.route('/health', methods=['GET'])
def get_redis_health():
    return jsonify(redis_health_service.redis_health)
