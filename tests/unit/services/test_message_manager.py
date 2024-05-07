from unittest import mock
from unittest.mock import MagicMock

import pytest

from backend.models.message import Message
from backend.services.message_manager import MessageManager
from backend.services.user_variable_manager import UserVariableManager


# Fixtures
@pytest.fixture
def user_variable_manager_mock():
    return MagicMock(spec=UserVariableManager)


@pytest.fixture
def message_manager(user_variable_manager_mock):
    return MessageManager(user_variable_manager=user_variable_manager_mock)


# Tests
def test_openai_client_lazy_initialization(message_manager, user_variable_manager_mock):
    with mock.patch("backend.services.message_manager.get_openai_client") as get_openai_client_mock:
        openai_client_mock = MagicMock()
        get_openai_client_mock.return_value = openai_client_mock

        assert message_manager._openai_client is None
        openai_client = message_manager.openai_client
        assert openai_client == openai_client_mock
        get_openai_client_mock.assert_called_once_with(user_variable_manager_mock)

        # Subsequent access should not call get_openai_client again
        openai_client = message_manager.openai_client
        assert openai_client == openai_client_mock
        get_openai_client_mock.assert_called_once()


def test_get_messages(message_manager):
    session_id = "test_session_id"
    limit = 10
    before = "2023-06-08T12:00:00Z"

    message_mock = MagicMock()
    message_mock.id = "message_id"
    message_mock.content = [MagicMock(text=MagicMock(value="message_content"))]
    message_mock.role = "user"
    message_mock.created_at = 1686225600  # Timestamp for 2023-06-08T12:00:00Z

    message_manager._openai_client = MagicMock()
    message_manager._openai_client.beta.threads.messages.list.return_value = [message_mock]

    messages = message_manager.get_messages(session_id, limit=limit, before=before)

    assert len(messages) == 1
    assert isinstance(messages[0], Message)
    assert messages[0].id == "message_id"
    assert messages[0].content == "message_content"
    assert messages[0].role == "user"
    assert messages[0].timestamp == "2023-06-08T12:00:00+00:00"
    assert messages[0].session_id == session_id

    message_manager._openai_client.beta.threads.messages.list.assert_called_once_with(
        thread_id=session_id,
        limit=limit,
        before=before,
        order="asc",
    )


def test_get_messages_no_content(message_manager):
    session_id = "test_session_id"

    message_mock = MagicMock()
    message_mock.id = "message_id"
    message_mock.content = []
    message_mock.role = "user"
    message_mock.created_at = 1686225600  # Timestamp for 2023-06-08T12:00:00Z

    message_manager._openai_client = MagicMock()
    message_manager._openai_client.beta.threads.messages.list.return_value = [message_mock]

    messages = message_manager.get_messages(session_id)

    assert len(messages) == 1
    assert messages[0].content == "[No content]"
