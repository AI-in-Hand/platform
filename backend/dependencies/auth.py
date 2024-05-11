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
    redis_cache_manager: RedisCacheManager = Depends(get_redis_cache_manager),
) -> User:
    token = credentials.credentials
    user_id = auth_service.get_user_id_from_token(token)
    
    # Check if the user is in the Redis cache
    cached_user = await redis_cache_manager.get(user_id)
    if cached_user:
        return User(**cached_user)
    
    # If not in cache, authenticate with Firebase
    user = auth_service.get_user(token)
    
    # Store the authenticated user in the Redis cache with a 5 minute expiration
    await redis_cache_manager.set(user_id, user.dict(), ex=300)
    
    return user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_superuser:
        logger.error(f"User {current_user.id} is not a superuser")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="The user doesn't have enough privileges")
    return current_user
