from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from openai.types.beta.threads import Text, TextDelta
from openai.types.beta.threads.runs import CodeInterpreterToolCall, CodeInterpreterToolCallDelta
from openai.types.beta.threads.runs.code_interpreter_tool_call import CodeInterpreter
from openai.types.beta.threads.runs.code_interpreter_tool_call_delta import CodeInterpreter as CodeInterpreterDelta


@pytest.mark.asyncio
async def test_on_text_delta(websocket_handler):
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
            event_handler_cls().on_text_delta(
                TextDelta(value="Sample delta"), Text(value="Sample text", annotations=[])
            )

        agency_mock.get_completion_stream.side_effect = get_completion_stream_mock

        get_messages_mock.return_value = []

        await websocket_handler._process_user_message(user, message_data, client_id)

        send_message_mock = websocket_handler.connection_manager.send_message
        assert (
            mock.call(
                {
                    "type": "agent_status",
                    "data": {"message": "Sample delta"},
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


@pytest.mark.asyncio
async def test_on_text_done(websocket_handler):
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
            event_handler_cls().on_text_done(Text(value="Sample text", annotations=[]))

        agency_mock.get_completion_stream.side_effect = get_completion_stream_mock

        get_messages_mock.return_value = []

        await websocket_handler._process_user_message(user, message_data, client_id)

        send_message_mock = websocket_handler.connection_manager.send_message
        assert (
            mock.call(
                {
                    "type": "agent_message",
                    "data": {
                        "sender": "Recipient",
                        "recipient": "Agent",
                        "message": {"content": "Sample text"},
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


@pytest.mark.asyncio
async def test_on_tool_call_created(websocket_handler):
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
            event_handler_cls().on_tool_call_created(
                CodeInterpreterToolCall(
                    id="123",
                    code_interpreter=CodeInterpreter(input="Sample input", outputs=[]),
                    type="code_interpreter",
                )
            )

        agency_mock.get_completion_stream.side_effect = get_completion_stream_mock

        get_messages_mock.return_value = []

        await websocket_handler._process_user_message(user, message_data, client_id)

        send_message_mock = websocket_handler.connection_manager.send_message
        assert (
            mock.call(
                {
                    "type": "agent_status",
                    "data": {"message": "\nRecipient > code_interpreter\n"},
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


@pytest.mark.asyncio
async def test_on_tool_call_delta(websocket_handler):
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
            event_handler_cls().on_tool_call_delta(
                CodeInterpreterToolCallDelta(
                    index=0,
                    type="code_interpreter",
                    input="Sample input",
                    outputs=[{"type": "logs", "logs": "Sample logs"}],
                    code_interpreter=CodeInterpreterDelta(input="Sample input", outputs=[]),
                ),
                MagicMock(),
            )

        agency_mock.get_completion_stream.side_effect = get_completion_stream_mock

        get_messages_mock.return_value = []

        await websocket_handler._process_user_message(user, message_data, client_id)

        send_message_mock = websocket_handler.connection_manager.send_message
        assert (
            mock.call(
                {
                    "type": "agent_status",
                    "data": {"message": "Sample input"},
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
