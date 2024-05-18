from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from openai.types.beta.threads import Text


@pytest.mark.asyncio
async def test_on_text_created(websocket_handler):
    user = MagicMock()
    message_data = {"content": "Sample message", "session_id": "sample_session_id"}
    client_id = "sample_client_id"

    with (
        patch.object(websocket_handler, "_setup_agency") as setup_agency_mock,
        patch.object(websocket_handler.message_manager, "get_messages") as get_messages_mock,
    ):
        agency_mock = MagicMock()
        setup_agency_mock.return_value = (MagicMock(), agency_mock)

        def get_completion_stream_mock(message, event_handler_cls):  # noqa: ARG001
            event_handler_cls.agent_name = "Agent"
            event_handler_cls.recipient_agent_name = "Recipient"
            event_handler_cls().on_text_created(Text(value="Sample text", annotations=[]))

        agency_mock.get_completion_stream.side_effect = get_completion_stream_mock

        get_messages_mock.return_value = []

        await websocket_handler._process_user_message(user, message_data, client_id)

        send_message_mock = websocket_handler.connection_manager.send_message
        assert (
            mock.call(
                {
                    "type": "agent_status",
                    "data": {
                        "message": "\nRecipient @ Agent  > ",
                    },
                },
                client_id,
            )
            in send_message_mock.await_args_list
        )
        assert (
            mock.call(
                {
                    "connection_id": "sample_client_id",
                    "type": "agent_response",
                    "data": {
                        "data": [],
                        "message": "Message processed successfully",
                        "status": True,
                    },
                },
                client_id,
            )
            in send_message_mock.await_args_list
        )
