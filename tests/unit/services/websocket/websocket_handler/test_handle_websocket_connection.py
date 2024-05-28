from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import AuthenticationError as OpenAIAuthenticationError
from starlette.websockets import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK

from backend.exceptions import NotFoundError, UnsetVariableError


@pytest.mark.asyncio
async def test_handle_websocket_connection(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"

    with patch.object(websocket_handler, "_handle_websocket_messages", new_callable=AsyncMock) as handle_messages_mock:
        handle_messages_mock.side_effect = WebSocketDisconnect(1000)
        await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.connect.assert_awaited_once_with(websocket, client_id)
    handle_messages_mock.assert_awaited_once_with(websocket, client_id)
    websocket_handler.connection_manager.disconnect.assert_awaited_once_with(client_id)


@pytest.mark.asyncio
async def test_handle_websocket_connection_unset_variable_error(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    expected_error_message = "Variable XXX is not set. Please set it first."

    with patch.object(websocket_handler, "_handle_websocket_messages", new_callable=AsyncMock) as handle_messages_mock:
        handle_messages_mock.side_effect = UnsetVariableError("XXX")
        await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": False, "message": expected_error_message}, client_id
    )


@pytest.mark.asyncio
async def test_handle_websocket_connection_openai_authentication_error(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    expected_error_message = "Authentication Error"
    response = MagicMock()
    body = {"error": "Authentication Error"}

    with patch.object(websocket_handler, "_handle_websocket_messages", new_callable=AsyncMock) as handle_messages_mock:
        handle_messages_mock.side_effect = OpenAIAuthenticationError(
            message=expected_error_message, response=response, body=body
        )
        await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": False, "message": expected_error_message}, client_id
    )


@pytest.mark.asyncio
async def test_handle_websocket_connection_not_found_error(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    expected_error_message = "Session not found: session_id"

    with patch.object(websocket_handler, "_handle_websocket_messages", new_callable=AsyncMock) as handle_messages_mock:
        handle_messages_mock.side_effect = NotFoundError("Session", id_="session_id")
        await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": False, "message": expected_error_message}, client_id
    )


@pytest.mark.asyncio
async def test_handle_websocket_connection_websocket_disconnect(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"

    with patch.object(websocket_handler, "_handle_websocket_messages", new_callable=AsyncMock) as handle_messages_mock:
        handle_messages_mock.side_effect = WebSocketDisconnect(1000)
        await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.disconnect.assert_awaited_once_with(client_id)


@pytest.mark.asyncio
async def test_handle_websocket_connection_connection_closed_ok(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"

    with patch.object(websocket_handler, "_handle_websocket_messages", new_callable=AsyncMock) as handle_messages_mock:
        handle_messages_mock.side_effect = ConnectionClosedOK(1000, "")
        await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.disconnect.assert_awaited_once_with(client_id)


@pytest.mark.asyncio
async def test_handle_websocket_connection_exception(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    expected_error_message = (
        "Something went wrong. We're investigating the issue. Please try again or report it using our chatbot widget."
    )

    with patch.object(websocket_handler, "_handle_websocket_messages", new_callable=AsyncMock) as handle_messages_mock:
        handle_messages_mock.side_effect = Exception("Some error")
        await websocket_handler.handle_websocket_connection(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": False, "message": expected_error_message}, client_id
    )


@pytest.mark.asyncio
async def test_handle_websocket_messages(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"

    with patch.object(websocket_handler, "_process_messages", new_callable=AsyncMock) as process_messages_mock:
        process_messages_mock.side_effect = [True, True, False]
        await websocket_handler._handle_websocket_messages(websocket, client_id)

    assert process_messages_mock.await_count == 3
    process_messages_mock.assert_awaited_with(websocket, client_id)
