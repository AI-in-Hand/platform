from datetime import UTC, datetime
from unittest import mock
from unittest.mock import MagicMock, patch

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
    return SessionManager(
        session_storage=session_storage_mock,
        user_variable_manager=MagicMock(),
        session_adapter=MagicMock(),
    )


# Tests
def test_create_session(agency_mock, session_manager, session_storage_mock):
    session_id = session_manager.create_session(agency_mock, "agency_id", "user_id", thread_ids={})
    assert session_id == "main_thread_id", "The session ID should be the ID of the main thread."
    expected_session_config = SessionConfig(
        id="main_thread_id",
        user_id="user_id",
        agency_id="agency_id",
        timestamp=datetime.now(UTC).isoformat(),
    )
    expected_session_config.timestamp = mock.ANY
    session_storage_mock.save.assert_called_once_with(expected_session_config)


def test_update_session_timestamp(session_manager, session_storage_mock):
    session_manager.update_session_timestamp("session_id")
    session_storage_mock.update.assert_called_once_with("session_id", {"timestamp": mock.ANY})


@patch("backend.services.session_manager.get_openai_client")
def test_delete_session(mock_openai_client, session_manager, session_storage_mock):
    session_manager.delete_session("session_id")
    session_storage_mock.delete.assert_called_once_with("session_id")
    mock_openai_client.return_value.beta.threads.delete.assert_called_once_with(thread_id="session_id", timeout=30.0)


def test_delete_sessions_by_agency_id(session_manager, session_storage_mock):
    session_manager.delete_sessions_by_agency_id("agency_id")
    session_storage_mock.delete_by_agency_id.assert_called_once_with("agency_id")


def test_get_sessions_for_user(session_manager, session_storage_mock):
    session_manager.get_sessions_for_user("user_id")
    session_storage_mock.load_by_user_id.assert_called_once_with("user_id")
