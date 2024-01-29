from unittest.mock import patch

import pytest
from fastapi import HTTPException, status
from jose import JWTError

from nalgonda.dependencies.auth import get_current_active_user, get_current_superuser, get_current_user
from nalgonda.models.auth import UserInDB
from nalgonda.settings import settings

user_data = {
    "username": "testuser",
    "disabled": False,
    "is_superuser": False,
    "id": "testuser",
    "hashed_password": "hashed_testpassword",
}
inactive_user_data = user_data.copy()
inactive_user_data["disabled"] = True

token_data = {"sub": "testuser"}


@pytest.fixture()
def mock_user_repository():
    with patch("nalgonda.repositories.user_repository.UserRepository.get_user_by_id") as mock:
        mock.return_value = user_data
        yield mock


@pytest.fixture()
def mock_jwt_decode():
    with patch("jose.jwt.decode") as mock:
        mock.return_value = token_data
        yield mock


@pytest.mark.asyncio
async def test_get_current_user_valid(mock_user_repository, mock_jwt_decode):
    user = await get_current_user("valid_token")
    assert user.username == user_data["username"]
    assert not user.disabled
    assert not user.is_superuser
    mock_user_repository.assert_called_once_with(user_data["username"])
    mock_jwt_decode.assert_called_once_with("valid_token", settings.secret_key, algorithms=["HS256"])


@pytest.mark.asyncio
async def test_get_current_user_invalid(mock_user_repository, mock_jwt_decode):
    mock_jwt_decode.side_effect = JWTError("Error decoding JWT")
    with pytest.raises(HTTPException) as exc:
        await get_current_user("invalid_token")
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    mock_user_repository.assert_not_called()
    mock_jwt_decode.assert_called_once_with("invalid_token", settings.secret_key, algorithms=["HS256"])


@pytest.mark.asyncio
async def test_get_current_active_user_disabled(mock_user_repository):
    with pytest.raises(HTTPException) as exc:
        await get_current_active_user(UserInDB(**inactive_user_data))
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    mock_user_repository.assert_not_called()


@pytest.mark.asyncio
async def test_get_current_superuser_not_superuser(mock_user_repository, mock_jwt_decode):
    user = UserInDB(**user_data)
    user.is_superuser = False
    with pytest.raises(HTTPException) as exc:
        await get_current_superuser(user)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    mock_user_repository.assert_not_called()
    mock_jwt_decode.assert_not_called()
