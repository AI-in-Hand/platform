import pytest

from backend.models.session_config import SessionConfig
from backend.repositories.session_storage import SessionConfigStorage
from tests.testing_utils import TEST_USER_ID


@pytest.fixture
def session_data():
    return {
        "id": "session1",
        "user_id": TEST_USER_ID,
        "agency_id": "agency1",
        "thread_ids": {},
        "timestamp": "2021-01-01T00:00:00Z",
    }


@pytest.fixture
def storage():
    return SessionConfigStorage()


def test_load_session_config_by_session_id(mock_firestore_client, session_data, storage):
    mock_firestore_client.setup_mock_data("session_configs", "session1", session_data)

    loaded_session_config = storage.load_by_id("session1")

    assert loaded_session_config is not None
    assert loaded_session_config.id == "session1"
    assert loaded_session_config.model_dump() == session_data


def test_load_session_config_by_user_id(mock_firestore_client, session_data, storage):
    # Setup mock data
    mock_firestore_client.setup_mock_data("session_configs", "session1", session_data)

    # Simulate loading session configs by user_id, reflecting the correct usage of `where()` before `stream()`
    loaded_sessions = storage.load_by_user_id(session_data["user_id"])

    assert loaded_sessions is not None
    # Verify that all loaded sessions have the correct user_id
    assert all(session.user_id == session_data["user_id"] for session in loaded_sessions)


def test_load_session_config_by_agency_id(mock_firestore_client, session_data, storage):
    # Setup mock data
    mock_firestore_client.setup_mock_data("session_configs", "session1", session_data)

    # Simulate loading session configs by agency_id, reflecting the correct usage of `where()` before `stream()`
    loaded_sessions = storage.load_by_agency_id(session_data["agency_id"])

    assert loaded_sessions is not None
    # Verify that all loaded sessions have the correct agency_id
    assert all(session.agency_id == session_data["agency_id"] for session in loaded_sessions)


def test_update_session_config(mock_firestore_client, session_data, storage):
    mock_firestore_client.setup_mock_data("session_configs", "session1", session_data)

    storage.update("session1", {"timestamp": "2021-01-02T00:00:00Z"})

    assert mock_firestore_client.to_dict()["timestamp"] == "2021-01-02T00:00:00Z"


def test_save_session_config(mock_firestore_client, session_data, storage):
    session_to_save = SessionConfig(**session_data)
    storage.save(session_to_save)

    assert mock_firestore_client.to_dict()["id"] == "session1"


def test_delete_session_config(mock_firestore_client, session_data, storage):
    mock_firestore_client.setup_mock_data("session_configs", "session1", session_data)

    storage.delete("session1")

    assert mock_firestore_client.to_dict() == {}
