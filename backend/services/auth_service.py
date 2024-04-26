import logging
from http import HTTPStatus

from fastapi import HTTPException
from firebase_admin import auth
from firebase_admin.exceptions import InvalidArgumentError, UnknownError

from backend.models.auth import User

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service class to handle Firebase authentication."""

    @classmethod
    def get_user(cls, token: str) -> User:
        try:
            decoded_token = auth.verify_id_token(token, check_revoked=True)
        except (ValueError, InvalidArgumentError, UnknownError) as err:
            logger.error(f"Invalid authentication credentials: {err}")
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
            ) from None
        logger.info(f"Authenticated user: {decoded_token['uid']}")
        return User(id=decoded_token["uid"], email=decoded_token["email"])
