import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.dependencies.dependencies import get_redis_cache_manager
from backend.models.auth import User
from backend.services.auth_service import AuthService
from backend.services.redis_cache_manager import RedisCacheManager

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(AuthService)],
    cache_manager: RedisCacheManager = Depends(get_redis_cache_manager)
) -> User:
    user_data = await cache_manager.get(credentials.credentials)
    if user_data:
        user = User.parse_obj(user_data)
    else:
        user = auth_service.get_user(credentials.credentials)
        await cache_manager.set(credentials.credentials, user.model_dump(), expire=300)

    return user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_superuser:
        logger.warning(f"User {current_user.id} is not a superuser")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="The user doesn't have enough privileges")
    return current_user
