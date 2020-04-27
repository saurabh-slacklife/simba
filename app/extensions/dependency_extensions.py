from app.services.user_service import UserService
from app.services.oauth_service import OAuthService
from app.services.redis_service import RedisHealthService
from app.services.client_service import ClientService
from app.client.http_request_client import HttpClient

user_service = UserService()
oauth_service = OAuthService()
client_service = ClientService()
redis_health_service = RedisHealthService()
http_client = HttpClient()
