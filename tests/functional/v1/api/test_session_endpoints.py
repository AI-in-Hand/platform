from unittest import mock
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.agency_manager import AgencyManager
from tests.testing_utils import TEST_USER_ID
from tests.testing_utils.constants import TEST_AGENCY_ID


@pytest.fixture
def session_config_data():
    return {
        "id": "test_session_id",
        "user_id": TEST_USER_ID,
        "agency_id": TEST_AGENCY_ID,
        "thread_ids": {},
        "timestamp": "2021-10-01T00:00:00Z",
    }


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_session_list(session_config_data, client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("session_configs", "test_session_id", session_config_data)
    agency_config = {"name": "Test agency", "id": TEST_AGENCY_ID, "main_agent": "test_agent_id"}
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_config)
    expected_session_data = session_config_data.copy()
    expected_session_data["flow_config"] = mock.ANY

    response = client.get("/api/v1/session/list")
    assert response.status_code == 200
    assert response.json()["data"] == [expected_session_data]


@pytest.mark.usefixtures("mock_get_current_user")
def test_create_session_success(client, mock_firestore_client):
    with patch.object(AgencyManager, "get_agency", AsyncMock(return_value=MagicMock())) as mock_get_agency:
        mock_get_agency.return_value.main_thread.id = "new_session_id"
        # mock Firestore to pass the security user_id check
        agency_config = {
            "id": TEST_AGENCY_ID,
            "name": "Test agency",
            "user_id": TEST_USER_ID,
            "main_agent": "test_agent_id",
        }
        mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_config)

        response = client.post(f"/api/v1/session?agency_id={TEST_AGENCY_ID}")
        # Assertions
        assert response.status_code == 200
        assert response.json()["data"] == [
            {
                "agency_id": TEST_AGENCY_ID,
                "id": "new_session_id",
                "thread_ids": mock.ANY,
                "timestamp": mock.ANY,
                "user_id": TEST_USER_ID,
                "flow_config": mock.ANY,
            }
        ]
        mock_get_agency.assert_awaited_once_with(TEST_AGENCY_ID, thread_ids={})

        # Check if the session config was created
        assert mock_firestore_client.collection("session_configs").to_dict() == {
            "id": "new_session_id",
            "user_id": TEST_USER_ID,
            "agency_id": TEST_AGENCY_ID,
            "thread_ids": {},
            "timestamp": mock.ANY,
        }


@pytest.mark.usefixtures("mock_get_current_user")
def test_create_session_agency_not_found(client, mock_firestore_client):
    with patch.object(AgencyManager, "get_agency", AsyncMock(return_value=None)):
        response = client.post("/api/v1/session?agency_id=test_session_id")
        assert response.status_code == 404
        assert response.json() == {"data": {"message": "Agency not found"}}
        assert mock_firestore_client.collection("session_configs").to_dict() == {}


@pytest.mark.usefixtures("mock_get_current_user")
def test_delete_session_success(client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("session_configs", "test_session_id", {"id": "test_session_id"})

    response = client.delete("/api/v1/session?id=test_session_id")
    assert response.status_code == 200
    assert response.json()["data"] == []
    # Check if the session config was deleted
    assert mock_firestore_client.collection("session_configs").to_dict() == {}
