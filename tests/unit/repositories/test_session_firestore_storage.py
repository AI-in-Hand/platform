import pytest

from backend.models.session_config import SessionConfig
from backend.repositories.session_firestore_storage import SessionConfigFirestoreStorage
from tests.test_utils import TEST_USER_ID


@pytest.fixture
def session_data():
    # Using an integer for the created_at field to align with the model definition
    return {
        "session_id": "session1",
        "user_id": TEST_USER_ID,
        "agency_id": "agency1",
        "created_at": 161803398874,  # Example integer timestamp
    }


@pytest.fixture
def storage():
    return SessionConfigFirestoreStorage()


def test_load_session_config_by_session_id(mock_firestore_client, session_data, storage):
    mock_firestore_client.setup_mock_data("session_configs", "session1", session_data)

    loaded_session_config = storage.load_by_session_id("session1")

    assert loaded_session_config is not None
    assert loaded_session_config.session_id == "session1"
    assert loaded_session_config.model_dump() == session_data


def test_load_session_config_by_user_id(mock_firestore_client, session_data, storage):
    # Setup mock data
    mock_firestore_client.setup_mock_data("session_configs", "session1", session_data)

    # Simulate loading session configs by user_id, reflecting the correct usage of `where()` before `stream()`
    loaded_sessions = storage.load_by_user_id(session_data["user_id"])

    assert loaded_sessions is not None
    # Verify that all loaded sessions have the correct user_id
    assert all(session.user_id == session_data["user_id"] for session in loaded_sessions)


def test_save_session_config(mock_firestore_client, session_data, storage):
    session_to_save = SessionConfig(**session_data)
    storage.save(session_to_save)

    assert mock_firestore_client.to_dict()["session_id"] == "session1"


def test_delete_session_config(mock_firestore_client, session_data, storage):
    mock_firestore_client.setup_mock_data("session_configs", "session1", session_data, doc_id="session1")

    storage.delete("session1")

    assert mock_firestore_client.to_dict() == {}
