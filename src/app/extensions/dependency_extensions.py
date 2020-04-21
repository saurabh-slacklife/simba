from src.app.services.user import UserService
from src.app.services.oauth.oauth_service import OAuthService
from src.app.services.redis_service import RedisHealthService

user_service = UserService()
oauth_service = OAuthService()
redis_health_service = RedisHealthService()

