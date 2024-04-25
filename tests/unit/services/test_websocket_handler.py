import asyncio
from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, WebSocket
from starlette.websockets import WebSocketDisconnect
from websockets import ConnectionClosedOK

from backend.services.websocket_handler import WebSocketHandler


@pytest.fixture
def websocket_handler():
    connection_manager = AsyncMock()
    auth_service = MagicMock()
    session_manager = MagicMock()
    agency_manager = AsyncMock()
    return WebSocketHandler(connection_manager, auth_service, session_manager, agency_manager)


@pytest.mark.asyncio
async def test_handle_websocket_connection(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    user_id = "user_id"
    agency_id = "agency_id"
    session_id = "session_id"

    websocket_handler.auth_service.get_user.return_value = None
    websocket_handler.session_manager.get_session.return_value = MagicMock()
    websocket_handler.agency_manager.get_agency.return_value = AsyncMock()

    with patch.object(websocket_handler, "_handle_websocket_messages", new_callable=AsyncMock) as handle_messages_mock:
        await websocket_handler.handle_websocket_connection(websocket, user_id, agency_id, session_id)

    websocket_handler.connection_manager.connect.assert_awaited_once_with(websocket)
    websocket_handler.auth_service.get_user.assert_called_once()
    websocket_handler.session_manager.get_session.assert_called_once_with(session_id)
    websocket_handler.agency_manager.get_agency.assert_awaited_once()
    handle_messages_mock.assert_awaited_once()
    websocket_handler.connection_manager.disconnect.assert_awaited_once_with(websocket)


@pytest.mark.asyncio
async def test_handle_websocket_connection_session_or_agency_not_found(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    user_id = "user_id"
    agency_id = "agency_id"
    session_id = "session_id"

    websocket_handler.auth_service.get_user.return_value = None
    websocket_handler.session_manager.get_session.return_value = None
    websocket_handler.agency_manager.get_agency.return_value = None

    await websocket_handler.handle_websocket_connection(websocket, user_id, agency_id, session_id)

    websocket_handler.connection_manager.send_message.assert_awaited_once_with("Session not found", websocket)
    websocket_handler.connection_manager.disconnect.assert_awaited_once_with(websocket)


@pytest.mark.asyncio
async def test_authenticate_success(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    user_id = "user_id"
    token = "valid_token"

    websocket.receive_text.return_value = token
    websocket_handler.auth_service.get_user.return_value = None

    await websocket_handler._authenticate(websocket, user_id)

    websocket.receive_text.assert_awaited_once()
    websocket_handler.auth_service.get_user.assert_called_once_with(token)
    websocket_handler.connection_manager.disconnect.assert_not_awaited()


@pytest.mark.asyncio
async def test_authenticate_invalid_token(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    user_id = "user_id"
    token = "invalid_token"

    websocket.receive_text.return_value = token
    websocket_handler.auth_service.get_user.side_effect = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
    )

    await websocket_handler._authenticate(websocket, user_id)

    websocket.receive_text.assert_awaited_once()
    websocket_handler.auth_service.get_user.assert_called_once_with(token)
    websocket_handler.connection_manager.send_message.assert_awaited_once_with("Invalid token", websocket)
    websocket_handler.connection_manager.disconnect.assert_awaited_once_with(websocket)


@pytest.mark.asyncio
async def test_setup_agency_session_not_found(websocket_handler):
    agency_id = "agency_id"
    user_id = "user_id"
    session_id = "session_id"

    websocket_handler.session_manager.get_session.return_value = None

    session_config, agency = await websocket_handler._setup_agency(agency_id, user_id, session_id)

    assert session_config is None
    assert agency is None


@pytest.mark.asyncio
async def test_handle_websocket_messages(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    agency_id = "agency_id"
    agency = AsyncMock()
    session_id = "session_id"
    user_id = "user_id"

    with patch.object(websocket_handler, "_process_messages", new_callable=AsyncMock) as process_messages_mock:
        process_messages_mock.side_effect = [True, True, False]
        await websocket_handler._handle_websocket_messages(websocket, agency_id, agency, session_id, user_id)

    assert process_messages_mock.await_count == 3
    process_messages_mock.assert_awaited_with(websocket, agency_id, agency, session_id, user_id)


@pytest.mark.asyncio
async def test_process_messages_websocket_disconnect(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    agency_id = "agency_id"
    agency = AsyncMock()
    session_id = "session_id"
    user_id = "user_id"

    with patch.object(
        websocket_handler, "_process_single_message", new_callable=AsyncMock
    ) as process_single_message_mock:
        process_single_message_mock.side_effect = WebSocketDisconnect(1000, "Disconnected")
        result = await websocket_handler._process_messages(websocket, agency_id, agency, session_id, user_id)

    assert result is False
    process_single_message_mock.assert_awaited_once_with(websocket, agency_id, agency, user_id)


@pytest.mark.asyncio
async def test_process_messages_connection_closed(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    agency_id = "agency_id"
    agency = AsyncMock()
    session_id = "session_id"
    user_id = "user_id"

    with patch.object(
        websocket_handler, "_process_single_message", new_callable=AsyncMock
    ) as process_single_message_mock:
        process_single_message_mock.side_effect = ConnectionClosedOK(1000, "Connection closed")
        result = await websocket_handler._process_messages(websocket, agency_id, agency, session_id, user_id)

    assert result is False
    process_single_message_mock.assert_awaited_once_with(websocket, agency_id, agency, user_id)


@pytest.mark.asyncio
async def test_process_messages_exception(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    agency_id = "agency_id"
    agency = AsyncMock()
    session_id = "session_id"
    user_id = "user_id"

    with patch.object(
        websocket_handler, "_process_single_message", new_callable=AsyncMock
    ) as process_single_message_mock:
        process_single_message_mock.side_effect = Exception("Some exception")
        result = await websocket_handler._process_messages(websocket, agency_id, agency, session_id, user_id)

    assert result is True
    process_single_message_mock.assert_awaited_once_with(websocket, agency_id, agency, user_id)
    websocket_handler.connection_manager.send_message.assert_awaited_once_with(
        "Something went wrong. Please try again.", websocket
    )


@pytest.mark.asyncio
async def test_process_single_message(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    agency_id = "agency_id"
    agency = AsyncMock()
    user_id = "user_id"
    user_message = "User message"

    websocket.receive_text.return_value = user_message

    with patch.object(
        websocket_handler, "_process_single_message_response", new_callable=AsyncMock
    ) as process_single_message_response_mock:
        process_single_message_response_mock.side_effect = [True, False]
        await websocket_handler._process_single_message(websocket, agency_id, agency, user_id)

    websocket.receive_text.assert_awaited_once()
    agency.get_completion.assert_called_once_with(message=user_message, yield_messages=True)
    assert process_single_message_response_mock.await_count == 2


@pytest.mark.asyncio
async def test_process_single_message_response_no_response(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    get_next_response = MagicMock(return_value=None)
    loop = asyncio.get_running_loop()

    result = await websocket_handler._process_single_message_response(get_next_response, websocket, loop)

    assert result is False
    get_next_response.assert_called_once()
    websocket_handler.connection_manager.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_single_message_response_with_response(websocket_handler):
    websocket = AsyncMock(spec=WebSocket)
    response = MagicMock()
    response.get_formatted_content.return_value = "Response text"
    get_next_response = MagicMock(return_value=response)
    loop = asyncio.get_running_loop()

    result = await websocket_handler._process_single_message_response(get_next_response, websocket, loop)

    assert result is True
    get_next_response.assert_called_once()
    websocket_handler.connection_manager.send_message.assert_awaited_once_with("Response text", websocket)
