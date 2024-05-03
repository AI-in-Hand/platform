from http import HTTPStatus
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException
from starlette.responses import Response

from backend.dependencies.middleware import UserContextMiddleware
from backend.models.auth import User
from backend.services.auth_service import AuthService
from backend.services.context_vars_manager import ContextEnvVarsManager


@pytest.mark.asyncio
async def test_no_authorization_header():
    request = Mock(headers={})
    call_next = AsyncMock(return_value=Response(status_code=200))

    middleware = UserContextMiddleware(app=None)
    response = await middleware.dispatch(request, call_next)

    call_next.assert_called_once()
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_invalid_token():
    with patch.object(AuthService, "get_user", side_effect=HTTPException(status_code=HTTPStatus.UNAUTHORIZED)):
        request = Mock(headers={"Authorization": "Bearer invalidtoken"})
        call_next = AsyncMock(return_value=Response())

        middleware = UserContextMiddleware(app=None)
        response = await middleware.dispatch(request, call_next)

        call_next.assert_called_once()
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_valid_token(caplog):
    caplog.set_level(10)

    user_mock = User(id="123", email="test_email")
    with (
        patch.object(AuthService, "get_user", return_value=user_mock),
        patch.object(ContextEnvVarsManager, "set") as mock_set,
    ):
        request = Mock(headers={"Authorization": "Bearer validtoken"})
        call_next = AsyncMock(return_value=Response())

        middleware = UserContextMiddleware(app=None)
        response = await middleware.dispatch(request, call_next)

        call_next.assert_called_once()
        mock_set.assert_called_with("user_id", "123")
        assert "Current User ID set in context: 123" in caplog.text
        assert response.status_code == 200
