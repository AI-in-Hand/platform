from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import WebSocket
from openai import AuthenticationError as OpenAIAuthenticationError
from starlette.websockets import WebSocketDisconnect
from websockets import ConnectionClosedOK

from backend.constants import INTERNAL_ERROR_MESSAGE
from backend.exceptions import NotFoundError, UnsetVariableError


@pytest.mark.asyncio
async def test_handle_websocket_connection(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    session_id = "session_id"
    token = "valid_token"

    websocket.receive_json.return_value = {
        "data": {
            "session_id": session_id,
        },
        "access_token": token,
    }
    websocket_handler.auth_service.get_user.return_value = MagicMock()
    websocket_handler.session_manager.get_session.return_value = MagicMock()
    websocket_handler.agency_manager.get_agency.return_value = (AsyncMock(), MagicMock())

    with patch.object(
        websocket_handler,
        "_handle_websocket_messages",
        new_callable=AsyncMock,
    ) as handle_messages_mock:
        await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.connect.assert_awaited_once_with(websocket, client_id)
    websocket_handler.auth_service.get_user.assert_called_once_with(token)
    websocket_handler.session_manager.get_session.assert_called_once_with(session_id)
    websocket_handler.agency_manager.get_agency.assert_awaited_once()
    handle_messages_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_websocket_connection_missing_fields(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"

    websocket.receive_json.return_value = {}

    await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": "error", "message": "Missing required fields"}, client_id
    )


@pytest.mark.asyncio
async def test_handle_websocket_connection_session_not_found(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    session_id = "session_id"
    token = "valid_token"

    websocket.receive_json.return_value = {
        "data": {
            "session_id": session_id,
        },
        "access_token": token,
    }
    websocket_handler.auth_service.get_user.return_value = MagicMock()
    websocket_handler.session_manager.get_session.side_effect = NotFoundError("Session", session_id)

    await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": "error", "message": "Session not found: session_id"}, client_id
    )


@pytest.mark.asyncio
async def test_handle_websocket_connection_agency_not_found(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    agency_id = "agency_id"
    session_id = "session_id"
    token = "valid_token"

    websocket.receive_json.return_value = {
        "data": {
            "session_id": session_id,
        },
        "access_token": token,
    }
    websocket_handler.auth_service.get_user.return_value = MagicMock()
    websocket_handler.session_manager.get_session.return_value = MagicMock()
    websocket_handler.agency_manager.get_agency.side_effect = NotFoundError("Agency", agency_id)

    await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": "error", "message": "Agency not found: agency_id"}, client_id
    )


@pytest.mark.asyncio
async def test_handle_websocket_connection_websocket_disconnect(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"

    websocket.receive_json.side_effect = WebSocketDisconnect(1000, "Disconnected")

    await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.disconnect.assert_awaited_once_with(client_id)


@pytest.mark.asyncio
async def test_handle_websocket_connection_connection_closed(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"

    websocket.receive_json.side_effect = ConnectionClosedOK(1000, "Connection closed")

    await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.disconnect.assert_awaited_once_with(client_id)


@pytest.mark.asyncio
async def test_handle_websocket_connection_unset_variable_error(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    session_id = "session_id"
    token = "valid_token"
    expected_error_message = "Variable Variable XXX not set is not set. Please set it first."

    websocket.receive_json.return_value = {
        "data": {
            "session_id": session_id,
        },
        "access_token": token,
    }
    websocket_handler.auth_service.get_user.side_effect = UnsetVariableError("Variable XXX not set")

    await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": "error", "message": expected_error_message}, client_id
    )


@pytest.mark.asyncio
async def test_handle_websocket_connection_openai_authentication_error(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    session_id = "session_id"
    token = "valid_token"
    expected_error_message = "Authentication Error"
    request = httpx.Request(method="GET", url="http://testserver/api/v1/agent?id=123")
    response = httpx.Response(401, request=request)

    websocket.receive_json.return_value = {
        "data": {
            "session_id": session_id,
        },
        "access_token": token,
    }
    websocket_handler.auth_service.get_user.side_effect = OpenAIAuthenticationError(
        expected_error_message, response=response, body={}
    )

    await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": "error", "message": expected_error_message}, client_id
    )


@pytest.mark.asyncio
async def test_handle_websocket_connection_not_found_error(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    session_id = "session_id"
    token = "valid_token"
    expected_error_message = "Session not found: session_id"

    websocket.receive_json.return_value = {
        "data": {
            "session_id": session_id,
        },
        "access_token": token,
    }
    websocket_handler.auth_service.get_user.return_value = MagicMock()
    websocket_handler.session_manager.get_session.side_effect = NotFoundError("Session", session_id)

    await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": "error", "message": expected_error_message}, client_id
    )


@pytest.mark.asyncio
async def test_handle_websocket_connection_exception(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    session_id = "session_id"
    token = "valid_token"

    websocket.receive_json.return_value = {
        "data": {
            "session_id": session_id,
        },
        "access_token": token,
    }
    websocket_handler.auth_service.get_user.side_effect = Exception("Some exception")

    await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {
            "status": "error",
            "message": INTERNAL_ERROR_MESSAGE,
        },
        client_id,
    )
