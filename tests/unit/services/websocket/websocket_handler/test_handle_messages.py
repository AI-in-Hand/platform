import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from openai import AuthenticationError as OpenAIAuthenticationError
from starlette.websockets import WebSocket

from backend.exceptions import NotFoundError, UnsetVariableError


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
    expected_error_message = "Variable Variable XXX not set is not set. Please set it first."

    with patch.object(
        websocket_handler, "_process_single_message", new_callable=AsyncMock
    ) as process_single_message_mock:
        process_single_message_mock.side_effect = UnsetVariableError("Variable XXX not set")
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
    request = httpx.Request(method="GET", url="http://testserver/api/v1/agent?id=123")
    response = httpx.Response(401, request=request)

    with patch.object(
        websocket_handler, "_process_single_message", new_callable=AsyncMock
    ) as process_single_message_mock:
        process_single_message_mock.side_effect = OpenAIAuthenticationError(
            expected_error_message, response=response, body={}
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
    session_id = "session_id"
    user_message = "User message"
    token = "token"

    websocket.receive_json.return_value = {
        "type": "user_message",
        "data": {"content": user_message, "session_id": session_id},
        "access_token": token,
    }

    with (
        patch.object(
            websocket_handler, "_process_single_message_response", new_callable=AsyncMock
        ) as process_single_message_response_mock,
        patch.object(websocket_handler, "_authenticate", new_callable=AsyncMock) as authenticate_mock,
        patch.object(websocket_handler, "_setup_agency", new_callable=AsyncMock) as setup_agency_mock,
    ):
        process_single_message_response_mock.side_effect = [True, False]
        setup_agency_mock.return_value = (MagicMock(), MagicMock())
        await websocket_handler._process_single_message(websocket, client_id)

    authenticate_mock.assert_awaited_once()
    setup_agency_mock.assert_awaited_once()
    process_single_message_response_mock.assert_awaited()


@pytest.mark.asyncio
async def test_process_single_message_empty_message(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    token = "token"

    websocket.receive_json.return_value = {"type": "user_message", "data": {"content": ""}, "access_token": token}

    with patch.object(websocket_handler, "_authenticate", new_callable=AsyncMock):
        await websocket_handler._process_single_message(websocket, client_id)

    websocket.receive_json.assert_awaited_once()
    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": False, "message": "Message or session ID not provided"}, client_id
    )


@pytest.mark.asyncio
async def test_process_single_message_invalid_message_type(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    token = "token"

    message = {"type": "invalid_type", "data": {}, "access_token": token}
    websocket.receive_json.return_value = message

    with patch.object(websocket_handler, "_authenticate", new_callable=AsyncMock):
        await websocket_handler._process_single_message(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": False, "message": "Invalid message type"}, client_id
    )


@pytest.mark.asyncio
async def test_process_single_message_response_no_response(websocket_handler):
    client_id = "client_id"
    get_next_response_func = MagicMock(return_value=None)
    loop = asyncio.get_running_loop()

    result = await websocket_handler._process_single_message_response(get_next_response_func, client_id, loop)

    assert result is False
    get_next_response_func.assert_called_once()
    websocket_handler.connection_manager.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_single_message_response_with_response(websocket_handler):
    client_id = "client_id"
    response = MagicMock()
    response.content = "Response text"
    get_next_response_func = MagicMock(return_value=response)
    loop = asyncio.get_running_loop()

    result = await websocket_handler._process_single_message_response(get_next_response_func, client_id, loop)

    assert result is True
    get_next_response_func.assert_called_once()
    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {
            "type": "agent_message",
            "data": {
                "sender": response.sender_name,
                "recipient": response.receiver_name,
                "message": {"content": "Response text"},
            },
        },
        client_id,
    )


@pytest.mark.asyncio
async def test_process_single_message_user_message_missing_token(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"

    message = {"type": "user_message", "data": {"content": "User message", "session_id": "session_id"}}
    websocket.receive_json.return_value = message

    await websocket_handler._process_single_message(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": False, "message": "Access token not provided"}, client_id
    )


@pytest.mark.asyncio
async def test_process_single_message_session_not_found(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    token = "token"
    session_id = "session_id"

    message = {
        "type": "user_message",
        "data": {"content": "User message", "session_id": session_id},
        "access_token": token,
    }
    websocket.receive_json.return_value = message

    with (
        patch.object(websocket_handler, "_authenticate", new_callable=AsyncMock),
        patch.object(websocket_handler, "_setup_agency", new_callable=AsyncMock, return_value=(None, None)),
    ):
        await websocket_handler._process_single_message(websocket, client_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        {"status": False, "message": "Session not found"}, client_id
    )


@pytest.mark.asyncio
async def test_process_single_message_agency_not_found(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    client_id = "client_id"
    token = "token"
    session_id = "session_id"

    message = {
        "type": "user_message",
        "data": {"content": "User message", "session_id": session_id},
        "access_token": token,
    }
    websocket.receive_json.return_value = message

    with (
        patch.object(websocket_handler, "_authenticate", new_callable=AsyncMock),
        patch.object(
            websocket_handler, "_setup_agency", new_callable=AsyncMock, side_effect=NotFoundError("Agency", "agency_id")
        ),
        pytest.raises(NotFoundError, match="Agency not found: agency_id"),
    ):
        await websocket_handler._process_single_message(websocket, client_id)
