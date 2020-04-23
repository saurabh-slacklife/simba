from app.services.user import UserService
from app.services.oauth.oauth_service import OAuthService
from app.services.redis_service import RedisHealthService

user_service = UserService()
oauth_service = OAuthService()
redis_health_service = RedisHealthService()

