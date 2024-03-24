import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth
from firebase_admin.exceptions import InvalidArgumentError, UnknownError

from nalgonda.models.auth import User

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> User:
    logger.info(f"Debugging: {credentials.credentials}")
    try:
        user = auth.verify_id_token(credentials.credentials, check_revoked=True)
        logger.info(f"Debugging: {user}")
    except (ValueError, InvalidArgumentError, UnknownError) as err:
        logger.error(f"Invalid authentication credentials: {err}")
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        ) from None
    logger.info(f"Authenticated user: {user['uid']} ({user['email']})")
    return User(id=user["uid"], email=user["email"])


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_superuser:
        logger.error(f"User {current_user.id} is not a superuser")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="The user doesn't have enough privileges")
    return current_user
