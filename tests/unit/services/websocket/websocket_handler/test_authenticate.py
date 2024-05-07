from http import HTTPStatus

import pytest
from fastapi import HTTPException
from starlette.websockets import WebSocketDisconnect


@pytest.mark.asyncio
async def test_authenticate_success(websocket_handler):
    client_id = "client_id"
    user_id = "user_id"
    token = "valid_token"

    websocket_handler.auth_service.get_user.return_value = None

    await websocket_handler._authenticate(client_id, user_id, token)

    websocket_handler.auth_service.get_user.assert_called_once_with(token)


@pytest.mark.asyncio
async def test_authenticate_invalid_token(websocket_handler):
    client_id = "client_id"
    user_id = "user_id"
    token = "invalid_token"

    websocket_handler.auth_service.get_user.side_effect = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
    )

    with pytest.raises(WebSocketDisconnect):
        await websocket_handler._authenticate(client_id, user_id, token)

    websocket_handler.auth_service.get_user.assert_called_once_with(token)
    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": "error", "message": "Invalid token"}, client_id
    )
