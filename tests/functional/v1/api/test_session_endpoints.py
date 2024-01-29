from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status

from nalgonda.models.request_models import ThreadPostRequest
from nalgonda.services.agency_manager import AgencyManager
from nalgonda.services.thread_manager import ThreadManager
from tests.test_utils import TEST_USER_ID


@pytest.mark.usefixtures("mock_get_current_active_user")
def test_create_session_success(client, mock_firestore_client):
    with patch.object(
        AgencyManager, "get_agency", AsyncMock(return_value=MagicMock())
    ) as mock_get_agency, patch.object(
        ThreadManager, "create_threads", MagicMock(return_value="new_thread_id")
    ) as mock_create_threads, patch.object(AgencyManager, "cache_agency", AsyncMock()) as mock_cache_agency:
        # mock Firestore to pass the security owner_id check
        mock_firestore_client.setup_mock_data(
            "agency_configs", "test_agency_id", {"name": "Test agency", "owner_id": TEST_USER_ID}
        )

        # Create request data
        request_data = ThreadPostRequest(agency_id="test_agency_id")
        # Create a test client
        response = client.post("/v1/api/session", json=request_data.model_dump())
        # Assertions
        assert response.status_code == 200
        assert response.json() == {"thread_id": "new_thread_id"}
        mock_get_agency.assert_awaited_once_with("test_agency_id", None)
        mock_create_threads.assert_called_once_with(mock_get_agency.return_value)
        mock_cache_agency.assert_awaited_once_with(mock_get_agency.return_value, "test_agency_id", "new_thread_id")


@pytest.mark.usefixtures("mock_get_current_active_user")
def test_create_session_agency_not_found(client):
    with patch.object(AgencyManager, "get_agency", AsyncMock(return_value=None)):
        # Create request data
        request_data = ThreadPostRequest(agency_id="test_agency_id")
        # Create a test client
        response = client.post("/v1/api/session", json=request_data.model_dump())
        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Agency not found"}


@pytest.fixture
def mock_get_agency():
    get_agency_mock = AsyncMock(return_value=MagicMock(get_completion=MagicMock(return_value="Hello, world!")))
    with patch.object(AgencyManager, "get_agency", get_agency_mock) as mock_get_agency:
        yield mock_get_agency


# Successful message sending
@pytest.mark.usefixtures("mock_get_current_active_user")
def test_post_agency_message_success(client, mock_get_agency, mock_firestore_client):
    agency_data = {"owner_id": "test_user_id", "agency_id": "test_agency_id", "name": "Test Agency"}
    mock_firestore_client.setup_mock_data("agency_configs", "test_agency_id", agency_data)

    # Sending a message
    message_data = {"agency_id": "test_agency_id", "thread_id": "test_thread_id", "message": "Hello, world!"}

    response = client.post("/v1/api/session/message", json=message_data)

    assert response.status_code == 200
    # We will check for the actual message we set up to be sent
    assert response.json().get("response") == "Hello, world!"
    mock_get_agency.assert_called_once_with("test_agency_id", "test_thread_id")


# Agency configuration not found
@pytest.mark.usefixtures("mock_get_current_active_user", "mock_firestore_client")
def test_post_agency_message_agency_config_not_found(client, mock_get_agency):
    # Sending a message
    message_data = {"agency_id": "test_agency", "thread_id": "test_thread", "message": "Hello, world!"}
    response = client.post("/v1/api/session/message", json=message_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Agency not found"
    mock_get_agency.assert_not_called()


# Current user not the owner of the agency
@pytest.mark.usefixtures("mock_get_current_active_user")
def test_post_agency_message_unauthorized(client, mock_get_agency, mock_firestore_client):
    agency_data = {"owner_id": "other_user_id", "agency_id": "test_agency", "name": "Test Agency"}
    mock_firestore_client.setup_mock_data("agency_configs", "test_agency", agency_data)

    # Sending a message
    message_data = {"agency_id": "test_agency", "thread_id": "test_thread", "message": "Hello, world!"}
    response = client.post("/v1/api/session/message", json=message_data)

    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"
    mock_get_agency.assert_not_called()


# Failure in message processing
@pytest.mark.usefixtures("mock_get_current_active_user")
def test_post_agency_message_processing_failure(client, mock_get_agency, mock_firestore_client):
    agency_data = {"owner_id": "test_user_id", "agency_id": "test_agency", "name": "Test Agency"}
    mock_firestore_client.setup_mock_data("agency_configs", "test_agency", agency_data)

    mock_get_agency.return_value.get_completion.side_effect = Exception("Test exception")

    # Sending a message
    message_data = {"agency_id": "test_agency", "thread_id": "test_thread", "message": "Hello, world!"}
    response = client.post("/v1/api/session/message", json=message_data)

    assert response.status_code == 500
    assert response.json()["detail"] == "Something went wrong"

    mock_get_agency.assert_called_once_with("test_agency", "test_thread")
