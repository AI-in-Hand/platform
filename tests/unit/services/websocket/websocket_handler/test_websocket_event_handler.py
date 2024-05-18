from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai.types.beta.threads import Text

from backend.services.websocket.websocket_handler import WebSocketHandler


@pytest.fixture
def websocket_handler():
    connection_manager = AsyncMock()
    auth_service = MagicMock()
    agency_manager = MagicMock()
    message_manager = MagicMock()
    session_manager = MagicMock()
    return WebSocketHandler(connection_manager, auth_service, agency_manager, message_manager, session_manager)


@pytest.mark.asyncio
async def test_on_text_created(websocket_handler):
    user = MagicMock()
    message_data = {"content": "Sample message", "session_id": "sample_session_id"}
    client_id = "sample_client_id"

    with (
        patch.object(websocket_handler, "_setup_agency") as setup_agency_mock,
        patch.object(websocket_handler.connection_manager, "send_message") as send_message_mock,
        patch.object(websocket_handler.message_manager, "get_messages") as get_messages_mock,
    ):
        setup_agency_mock.return_value = (MagicMock(), MagicMock())

        agency_mock = MagicMock()
        setup_agency_mock.return_value = (MagicMock(), agency_mock)

        async def get_completion_stream_mock(message, event_handler):  # noqa
            event_handler.agent_name = "Agent"
            event_handler.recipient_agent_name = "Recipient"
            event_handler.on_text_created(Text(value="Sample text"))

        agency_mock.get_completion_stream.side_effect = get_completion_stream_mock

        get_messages_mock.return_value = []

        await websocket_handler._process_user_message(user, message_data, client_id)

        send_message_mock.assert_any_call(
            {
                "type": "agent_status",
                "data": {"message": "\nRecipient @ Agent  > "},
            },
            client_id,
        )
        send_message_mock.assert_called_with(
            {
                "type": "agent_response",
                "data": {"status": True, "message": "Message processed successfully", "data": []},
                "connection_id": client_id,
            },
            client_id,
        )
