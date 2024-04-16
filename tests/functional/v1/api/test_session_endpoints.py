from unittest import mock
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.agency_manager import AgencyManager
from backend.services.session_manager import SessionManager
from tests.testing_utils import TEST_USER_ID
from tests.testing_utils.constants import TEST_AGENCY_ID


@pytest.fixture
def session_config_data():
    return {
        "id": "test_session_id",
        "user_id": TEST_USER_ID,
        "agency_id": TEST_AGENCY_ID,
        "timestamp": "2021-10-01T00:00:00Z",
    }


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_session_list(session_config_data, client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("session_configs", "test_session_id", session_config_data)
    mock_firestore_client.setup_mock_data(
        "agency_configs", TEST_AGENCY_ID, {"name": "Test agency", "id": TEST_AGENCY_ID}
    )
    expected_session_data = session_config_data.copy()
    expected_session_data["flow_config"] = mock.ANY

    response = client.get("/api/v1/session/list")
    assert response.status_code == 200
    assert response.json()["data"] == [expected_session_data]


@pytest.mark.usefixtures("mock_get_current_user")
def test_create_session_success(client, mock_firestore_client):
    with (
        patch.object(AgencyManager, "get_agency", AsyncMock(return_value=MagicMock())) as mock_get_agency,
        patch.object(
            SessionManager, "_create_threads", MagicMock(return_value="new_session_id")
        ) as mock_create_threads,
    ):
        # mock Firestore to pass the security user_id check
        mock_firestore_client.setup_mock_data(
            "agency_configs", TEST_AGENCY_ID, {"id": TEST_AGENCY_ID, "name": "Test agency", "user_id": TEST_USER_ID}
        )

        response = client.post(f"/api/v1/session?agency_id={TEST_AGENCY_ID}")
        # Assertions
        assert response.status_code == 200
        assert response.json()["data"] == [
            {
                "agency_id": TEST_AGENCY_ID,
                "id": "new_session_id",
                "timestamp": mock.ANY,
                "user_id": TEST_USER_ID,
                "flow_config": mock.ANY,
            }
        ]
        mock_get_agency.assert_awaited_once_with(TEST_AGENCY_ID)
        mock_create_threads.assert_called_once_with(mock_get_agency.return_value)

        # Check if the session config was created
        assert mock_firestore_client.collection("session_configs").to_dict() == {
            "id": "new_session_id",
            "user_id": TEST_USER_ID,
            "agency_id": TEST_AGENCY_ID,
            "timestamp": mock.ANY,
        }


@pytest.mark.usefixtures("mock_get_current_user")
def test_create_session_agency_not_found(client):
    with patch.object(AgencyManager, "get_agency", AsyncMock(return_value=None)):
        response = client.post("/api/v1/session?agency_id=test_session_id")
        assert response.status_code == 404
        assert response.json() == {"data": {"message": "Agency not found"}}


@pytest.mark.usefixtures("mock_get_current_user")
def test_delete_session_success(client):
    with patch.object(SessionManager, "delete_session", MagicMock()) as mock_delete_session:
        response = client.delete("/api/v1/session?id=test_session_id")
        assert response.status_code == 200
        mock_delete_session.assert_called_once_with("test_session_id")
