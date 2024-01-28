from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status

from nalgonda.models.request_models import ThreadPostRequest
from nalgonda.services.agency_manager import AgencyManager
from nalgonda.services.thread_manager import ThreadManager
from tests.test_utils import TEST_USER_ID


def test_create_session_success(client, mock_firestore_client, mock_get_current_active_user):  # noqa: ARG001
    with patch.object(
        AgencyManager, "get_agency", AsyncMock(return_value=MagicMock())
    ) as mock_get_agency, patch.object(
        ThreadManager, "create_threads", MagicMock(return_value="new_session_id")
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
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"session_id": "new_session_id"}
        mock_get_agency.assert_awaited_once_with("test_agency_id", None)
        mock_create_threads.assert_called_once_with(mock_get_agency.return_value)
        mock_cache_agency.assert_awaited_once_with(mock_get_agency.return_value, "test_agency_id", "new_session_id")


def test_create_session_agency_not_found(client, mock_get_current_active_user):  # noqa: ARG001
    with patch.object(AgencyManager, "get_agency", AsyncMock(return_value=None)):
        # Create request data
        request_data = ThreadPostRequest(agency_id="test_agency_id")
        # Create a test client
        response = client.post("/v1/api/session", json=request_data.model_dump())
        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Agency not found"}
