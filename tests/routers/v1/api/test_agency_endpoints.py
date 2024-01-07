from unittest.mock import AsyncMock, patch

from nalgonda.models.agency_config import AgencyConfig


def test_get_agency_config(client, mock_firestore_client):
    mock_data = {
        "agency_id": "test_agency",
        "owner_id": "test_owner",
        "agency_manifesto": "Test Manifesto",
        "agents": [],
        "agency_chart": [],
    }
    mock_firestore_client.setup_mock_data("agency_configs", "test_agency", mock_data)

    response = client.get("/v1/api/agency/config?agency_id=test_agency")
    assert response.status_code == 200
    assert response.json() == mock_data


def test_update_agency_config_success(client, mock_firestore_client):
    # Setup initial data in mock Firestore client
    initial_data = {
        "agency_id": "test_agency",
        "owner_id": "test_owner",
        "agency_manifesto": "Original Manifesto",
        "agents": [],
        "agency_chart": [],
    }
    mock_firestore_client.setup_mock_data("agency_configs", "test_agency", initial_data)
    new_data = {"agency_manifesto": "Updated Manifesto"}

    with patch(
        "nalgonda.dependencies.agency_manager.AgencyManager.update_agency", new_callable=AsyncMock
    ) as mock_update_agency:
        response = client.put("/v1/api/agency/config?agency_id=test_agency", json=new_data)

    mock_update_agency.assert_called_once_with(AgencyConfig.model_validate(initial_data), new_data)

    assert response.status_code == 200
    assert response.json() == {"message": "Agency configuration updated successfully"}


def test_get_agency_config_not_found(client, mock_firestore_client):  # noqa: ARG001
    # Simulate non-existent agency by not setting up any data for it
    response = client.get("/v1/api/agency/config?agency_id=non_existent_agency")
    assert response.status_code == 404
    assert response.json() == {"detail": "Agency configuration not found"}
