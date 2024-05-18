from http import HTTPStatus

import pytest
from fastapi import HTTPException
from starlette.websockets import WebSocketDisconnect

from backend.models.auth import User


@pytest.mark.asyncio
async def test_authenticate_valid_token(websocket_handler):
    client_id = "client_id"
    token = "valid_token"

    user = User(id="user_id", email="user@example.com")
    websocket_handler.auth_service.get_user.return_value = user

    result = await websocket_handler._authenticate(client_id, token)

    assert result == user
    websocket_handler.auth_service.get_user.assert_called_once_with(token)


@pytest.mark.asyncio
async def test_authenticate_invalid_token(websocket_handler):
    client_id = "client_id"
    token = "invalid_token"

    websocket_handler.auth_service.get_user.side_effect = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
    )

    with pytest.raises(WebSocketDisconnect):
        await websocket_handler._authenticate(client_id, token)

    websocket_handler.auth_service.get_user.assert_called_once_with(token)
    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": False, "message": "Invalid token"}, client_id
    )
