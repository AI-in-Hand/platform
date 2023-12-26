from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from nalgonda.models.auth import TokenData, User, UserInDB
from nalgonda.settings import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# TODO: Move this to a database
users_db = {
    "voiceflow_ainhand": {
        "username": "voiceflow_ainhand",
        "hashed_password": "$2b$12$o8As6pJtE5tvk/pFdTplSeCkIv9ScbliW7sy4yWXS4bjre77ZDKUG",
        "disabled": False,
    }
}


def get_user(db, username: str) -> UserInDB | None:
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception from None
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
