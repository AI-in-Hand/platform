import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from nalgonda.models.auth import TokenData, UserInDB
from nalgonda.repositories.user_repository import UserRepository
from nalgonda.settings import settings

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/api/token")


def get_user(username: str) -> UserInDB | None:
    user = UserRepository().get_user_by_id(username)
    if user:
        return UserInDB(**user)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            logger.error(f"Invalid token: {token}")
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        logger.error(f"Invalid token: {token}")
        raise credentials_exception from None
    user = get_user(username=token_data.username)
    if user is None:
        logger.error(f"User not found: {token_data.username}, token: {token}")
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserInDB, Depends(get_current_user)],
) -> UserInDB:
    if current_user.disabled:
        logger.error(f"User {current_user.id} is inactive")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


async def get_current_superuser(
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
) -> UserInDB:
    if not current_user.is_superuser:
        logger.error(f"User {current_user.id} is not a superuser")
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges")
    return current_user
