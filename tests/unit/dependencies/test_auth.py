from typing import Any
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from firebase_admin.auth import (
    CertificateFetchError,
    ExpiredIdTokenError,
    InvalidIdTokenError,
    RevokedIdTokenError,
    UserDisabledError,
)

from backend.dependencies.auth import get_current_superuser, get_current_user
from backend.models.auth import User

user_data: dict[str, Any] = {
    "uid": "testuser",
    "email": "testuser@example.com",
}


@pytest.fixture()
def mock_verify_id_token():
    with patch("backend.dependencies.auth.auth.verify_id_token") as mock:
        mock.return_value = user_data
        yield mock


@pytest.mark.asyncio
async def test_get_current_user_valid(mock_verify_id_token):
    user = await get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token"))
    assert user.id == user_data["uid"]
    assert not user.is_superuser
    mock_verify_id_token.assert_called_once_with("valid_token", check_revoked=True)


@pytest.mark.parametrize(
    "exception",
    [
        ValueError("Invalid token"),
        InvalidIdTokenError("Invalid token"),
        ExpiredIdTokenError("Expired token", cause="Expired token"),
        RevokedIdTokenError("Revoked token"),
        CertificateFetchError("Error fetching certificate", cause="Error fetching certificate"),
        UserDisabledError("User is disabled"),
    ],
)
@pytest.mark.asyncio
async def test_get_current_user_invalid(mock_verify_id_token, exception):
    mock_verify_id_token.side_effect = exception
    with pytest.raises(HTTPException) as exc:
        await get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token"))
        assert exc.value.status_code == 401
    mock_verify_id_token.assert_called_once_with("invalid_token", check_revoked=True)


@pytest.mark.asyncio
async def test_get_current_superuser_not_superuser(mock_verify_id_token):
    user = User(id=user_data["uid"], email=user_data["email"])
    user.is_superuser = False
    with pytest.raises(HTTPException) as exc:
        await get_current_superuser(user)
    assert exc.value.status_code == 403
    mock_verify_id_token.assert_not_called()
