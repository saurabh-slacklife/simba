from main.app.services.user import UserService
from main.app.services.oauth.oauth_service import OAuthService
from main.app.services.redis_service import RedisHealthService

user_service = UserService()
oauth_service = OAuthService()
redis_health_service = RedisHealthService()

