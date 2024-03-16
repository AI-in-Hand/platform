from datetime import UTC, datetime
from unittest.mock import MagicMock, call, patch

import pytest

from nalgonda.models.session_config import SessionConfig
from nalgonda.services.session_manager import SessionManager


# Fixtures
@pytest.fixture
def agency_mock():
    agency = MagicMock()
    agency.main_thread.id = "main_thread_id"
    return agency


@pytest.fixture
def env_config_storage_mock():
    return MagicMock()


@pytest.fixture
def session_storage_mock():
    return MagicMock()


@pytest.fixture
def session_manager(env_config_storage_mock, session_storage_mock):
    return SessionManager(env_config_storage=env_config_storage_mock, session_storage=session_storage_mock)


@pytest.fixture
def agent_mock():
    return MagicMock()


@pytest.fixture
def recipient_agent_mock():
    return MagicMock()


@pytest.fixture
def thread_mock():
    return MagicMock()


# Helper function for creating a mock thread
def create_mock_thread(agent, recipient_agent, id="thread_id"):
    thread = MagicMock()
    thread.agent = agent
    thread.recipient_agent = recipient_agent
    thread.id = id
    return thread


# Tests
def test_create_session(agency_mock, session_manager, session_storage_mock):
    # Mock _create_thread to return a mock object with an id attribute
    session_manager._create_thread = MagicMock(return_value=MagicMock(id="main_thread_id"))

    with patch("nalgonda.services.session_manager.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = datetime(2021, 1, 1, tzinfo=UTC)
        session_id = session_manager.create_session(agency_mock, "agency_id", "owner_id")

    assert session_id == "main_thread_id", "The session ID should be the ID of the main thread."
    expected_session_config = SessionConfig(
        session_id="main_thread_id",
        owner_id="owner_id",
        agency_id="agency_id",
        created_at=int(datetime(2021, 1, 1).timestamp()),
    )
    session_storage_mock.save.assert_called_once_with(expected_session_config)


@patch("nalgonda.services.session_manager.get_openai_client")
def test_create_threads(mock_get_openai_client, session_manager, agency_mock):
    mock_client = MagicMock()
    mock_get_openai_client.return_value = mock_client

    with patch.object(session_manager, "_init_threads") as mock_init_threads:
        session_id = session_manager._create_threads(agency_mock)

    mock_init_threads.assert_called_once_with(agency_mock, mock_client)
    assert session_id == agency_mock.main_thread.id, "Session ID should match the main thread ID."


def test_init_threads(session_manager, agency_mock, agent_mock, recipient_agent_mock):
    client_mock = MagicMock()
    agency_mock.agents_and_threads = {
        agent_mock: {recipient_agent_mock: None},
    }
    agency_mock.agents = {agent_mock: agent_mock, recipient_agent_mock: recipient_agent_mock}
    agency_mock.user = agent_mock
    agency_mock.ceo = recipient_agent_mock

    with patch.object(session_manager, "_create_thread") as mock_create_thread:
        session_manager._init_threads(agency_mock, client_mock)

    # Verify _create_thread is called for each agent pair and for the user-ceo main thread
    expected_calls = [
        call(agent_mock, recipient_agent_mock, client_mock),
        call(agent_mock, recipient_agent_mock, client_mock),  # Main thread
    ]
    mock_create_thread.assert_has_calls(expected_calls, any_order=True)


@patch("nalgonda.services.session_manager.Thread")
def test_create_thread(mock_thread_class, session_manager, agent_mock, recipient_agent_mock):
    client_mock = MagicMock()
    mock_thread_instance = create_mock_thread(agent_mock, recipient_agent_mock)
    mock_thread_class.return_value = mock_thread_instance

    new_thread = session_manager._create_thread(agent_mock, recipient_agent_mock, client_mock)

    assert new_thread == mock_thread_instance, "The created thread should be returned."
    mock_thread_class.assert_called_once_with(agent_mock, recipient_agent_mock)
