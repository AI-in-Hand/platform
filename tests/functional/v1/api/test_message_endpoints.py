from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.agency_manager import AgencyManager
from tests.test_utils import TEST_USER_ID
from tests.test_utils.constants import TEST_AGENCY_ID


@pytest.fixture
def mock_get_agency():
    get_agency_mock = AsyncMock(return_value=MagicMock(get_completion=MagicMock(return_value="Hello, world!")))
    with patch.object(AgencyManager, "get_agency", get_agency_mock) as mock_get_agency:
        yield mock_get_agency


# Successful message sending
@pytest.mark.usefixtures("mock_get_current_user")
def test_post_agency_message_success(client, mock_get_agency, mock_firestore_client):
    agency_data = {"user_id": TEST_USER_ID, "id": TEST_AGENCY_ID, "name": "Test Agency"}
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_data)

    # Sending a message
    message_data = {"agency_id": TEST_AGENCY_ID, "session_id": "test_session_id", "message": "Hello, world!"}

    response = client.post("/v1/api/message", json=message_data)

    assert response.status_code == 200
    # We will check for the actual message we set up to be sent
    assert response.json().get("response") == "Hello, world!"
    mock_get_agency.assert_called_once_with(TEST_AGENCY_ID, "test_session_id")


# Agency configuration not found
@pytest.mark.usefixtures("mock_get_current_user", "mock_firestore_client")
def test_post_agency_message_agency_config_not_found(client, mock_get_agency):
    # Sending a message
    message_data = {"agency_id": "test_agency", "session_id": "test_session_id", "message": "Hello, world!"}
    response = client.post("/v1/api/message", json=message_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Agency not found"
    mock_get_agency.assert_not_called()


# Current user not the owner of the agency
@pytest.mark.usefixtures("mock_get_current_user")
def test_post_agency_message_unauthorized(client, mock_get_agency, mock_firestore_client):
    agency_data = {"user_id": "other_user_id", "id": "test_agency", "name": "Test Agency"}
    mock_firestore_client.setup_mock_data("agency_configs", "test_agency", agency_data)

    # Sending a message
    message_data = {"agency_id": "test_agency", "session_id": "test_session_id", "message": "Hello, world!"}
    response = client.post("/v1/api/message", json=message_data)

    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"
    mock_get_agency.assert_not_called()


# Failure in message processing
@pytest.mark.usefixtures("mock_get_current_user")
def test_post_agency_message_processing_failure(client, mock_get_agency, mock_firestore_client):
    agency_data = {"user_id": TEST_USER_ID, "id": "test_agency", "name": "Test Agency"}
    mock_firestore_client.setup_mock_data("agency_configs", "test_agency", agency_data)

    mock_get_agency.return_value.get_completion.side_effect = Exception("Test exception")

    # Sending a message
    message_data = {"agency_id": "test_agency", "session_id": "test_session_id", "message": "Hello, world!"}
    response = client.post("/v1/api/message", json=message_data)

    assert response.status_code == 500
    assert response.json()["detail"] == "Something went wrong"

    mock_get_agency.assert_called_once_with("test_agency", "test_session_id")


@pytest.fixture
def mock_session_storage(mock_firestore_client):
    session_data = {
        "session_id": "test_session_id",
        "user_id": TEST_USER_ID,
        "agency_id": TEST_AGENCY_ID,
        "created_at": 1234567890,
    }
    mock_firestore_client.setup_mock_data("session_configs", "test_session_id", session_data)


@pytest.fixture
def mock_openai_client():
    with patch("backend.routers.v1.api.message.get_openai_client") as mock:
        mock.return_value.beta.threads.messages.list.return_value = ["Message 1", "Message 2"]
        yield mock


# Successful retrieval of messages
@pytest.mark.usefixtures("mock_get_current_user", "mock_session_storage", "mock_openai_client")
def test_get_message_list_success(client):
    response = client.get("/v1/api/message/list?session_id=test_session_id")
    assert response.status_code == 200
    assert len(response.json()) == 2  # Assuming the mock returns a list of 2 messages


# Session not found
@pytest.mark.usefixtures("mock_get_current_user", "mock_openai_client")
def test_get_message_list_session_not_found(client):
    response = client.get("/v1/api/message/list?session_id=nonexistent_session_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


# Current user not authorized
@pytest.mark.usefixtures("mock_get_current_user", "mock_session_storage", "mock_openai_client")
def test_get_message_list_unauthorized(client, mock_firestore_client):
    test_session_config = {
        "session_id": "test_session_id",
        "user_id": "other_user_id",
        "agency_id": TEST_AGENCY_ID,
        "created_at": 1234567890,
    }
    mock_firestore_client.setup_mock_data("session_configs", "test_session_id", test_session_config)

    response = client.get("/v1/api/message/list?session_id=test_session_id")
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"
