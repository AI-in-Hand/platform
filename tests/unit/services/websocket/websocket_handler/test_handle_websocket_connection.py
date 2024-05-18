from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import AuthenticationError as OpenAIAuthenticationError
from starlette.websockets import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK

from backend.exceptions import NotFoundError, UnsetVariableError
from backend.models.auth import User
from backend.models.message import Message
from backend.models.session_config import SessionConfig


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


@pytest.mark.asyncio
async def test_process_messages_unset_variable_error(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    expected_error_message = "Variable XXX is not set. Please set it first."

    with patch.object(
        websocket_handler, "_process_single_message", new_callable=AsyncMock
    ) as process_single_message_mock:
        process_single_message_mock.side_effect = UnsetVariableError("XXX")
        result = await websocket_handler._process_messages(websocket, client_id)

    assert result is False
    process_single_message_mock.assert_awaited_once_with(websocket, client_id)
    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": False, "message": expected_error_message}, client_id
    )


@pytest.mark.asyncio
async def test_process_messages_openai_authentication_error(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    expected_error_message = "Authentication Error"
    response = MagicMock()
    body = {"error": "Authentication Error"}

    with patch.object(
        websocket_handler, "_process_single_message", new_callable=AsyncMock
    ) as process_single_message_mock:
        process_single_message_mock.side_effect = OpenAIAuthenticationError(
            message=expected_error_message, response=response, body=body
        )
        result = await websocket_handler._process_messages(websocket, client_id)

    assert result is False
    process_single_message_mock.assert_awaited_once_with(websocket, client_id)
    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": False, "message": expected_error_message}, client_id
    )


@pytest.mark.asyncio
async def test_process_single_message_user_message(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    user_message = "User message"
    session_id = "session_id"
    token = "valid_token"
    user = User(id="user_id", email="user@example.com")
    session = SessionConfig(
        id="session_id",
        name="Session",
        user_id=user.id,
        agency_id="agency_id",
        thread_ids={"thread1": "thread1", "thread2": "thread2"},
    )
    agency = MagicMock()
    all_messages = [
        Message(content="Message 1", session_id=session_id),
        Message(content="Message 2", session_id=session_id),
    ]

    websocket.receive_json.return_value = {
        "type": "user_message",
        "data": {"content": user_message, "session_id": session_id},
        "access_token": token,
    }
    websocket_handler.auth_service.get_user.return_value = user
    websocket_handler.session_manager.get_session.return_value = session
    websocket_handler.agency_manager.get_agency.return_value = (agency, None)
    websocket_handler.message_manager.get_messages.return_value = all_messages

    await websocket_handler._process_single_message(websocket, client_id)

    websocket.receive_json.assert_awaited_once()
    websocket_handler.auth_service.get_user.assert_called_once_with(token)
    websocket_handler.session_manager.get_session.assert_called_once_with(session_id)
    websocket_handler.agency_manager.get_agency.assert_awaited_once_with(session.agency_id, session.thread_ids, user.id)
    websocket_handler.session_manager.update_session_timestamp.assert_called_once_with(session_id)
    websocket_handler.message_manager.get_messages.assert_called_once_with(session_id)
    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {
            "type": "agent_response",
            "data": {
                "status": True,
                "message": "Message processed successfully",
                "data": [message.model_dump() for message in all_messages],
            },
            "connection_id": client_id,
        },
        client_id,
    )


@pytest.mark.asyncio
async def test_process_single_message_invalid_message_type(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    token = "valid_token"

    websocket.receive_json.return_value = {"type": "invalid_type", "data": {}, "access_token": token}

    await websocket_handler._process_single_message(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": False, "message": "Invalid message type"}, client_id
    )
