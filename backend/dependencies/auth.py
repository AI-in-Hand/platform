import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.models.auth import User
from backend.services.auth_service import AuthService

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    authentication_manager: Annotated[AuthService, Depends(AuthService)],
) -> User:
    return authentication_manager.get_user(credentials.credentials)


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_superuser:
        logger.error(f"User {current_user.id} is not a superuser")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="The user doesn't have enough privileges")
    return current_user
