from datetime import UTC, datetime
from unittest import mock
from unittest.mock import MagicMock, call

import pytest

from backend.models.session_config import SessionConfig
from backend.services.session_manager import SessionManager


# Fixtures
@pytest.fixture
def agency_mock():
    agency = MagicMock()
    agency.main_thread.id = "main_thread_id"
    return agency


@pytest.fixture
def session_storage_mock():
    return MagicMock()


@pytest.fixture
def session_manager(session_storage_mock):
    return SessionManager(user_secret_manager=MagicMock(), session_storage=session_storage_mock)


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

    session_id = session_manager.create_session(agency_mock, "agency_id", "user_id", thread_ids={})

    assert session_id == "main_thread_id", "The session ID should be the ID of the main thread."
    expected_session_config = SessionConfig(
        id="main_thread_id",
        user_id="user_id",
        agency_id="agency_id",
        timestamp=datetime.now(UTC).isoformat(),
    )
    expected_session_config.timestamp = mock.ANY
    assert session_storage_mock.save.call_args_list == [call(expected_session_config)]


def test_delete_session(session_manager, session_storage_mock):
    session_manager.delete_session("session_id")

    assert session_storage_mock.delete.call_args_list == [call("session_id")]


def test_delete_sessions_by_agency_id(session_manager, session_storage_mock):
    session_manager.delete_sessions_by_agency_id("agency_id")

    assert session_storage_mock.delete_by_agency_id.call_args_list == [call("agency_id")]
