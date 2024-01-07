from unittest.mock import patch

from nalgonda.models.agency_config import AgencyConfig
from nalgonda.persistence.agency_config_firestore_storage import AgencyConfigFirestoreStorage


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


@patch.object(AgencyConfigFirestoreStorage, "save")
def test_update_agency_config_success(mock_save, client, mock_firestore_client):
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
    response = client.put("/v1/api/agency/config?agency_id=test_agency", json=new_data)

    assert response.status_code == 200
    assert response.json() == {"message": "Agency configuration updated successfully"}

    # Verify that the save method was called with the updated configuration
    updated_config = AgencyConfig(
        agency_id="test_agency",
        owner_id="test_owner",
        agency_manifesto="Updated Manifesto",
        agents=[],
        agency_chart=[],
    )
    mock_save.assert_called_once_with(updated_config)


def test_get_agency_config_not_found(client, mock_firestore_client):
    # Ensure no data is set in the mock Firestore client for the non-existent agency
    mock_firestore_client.setup_mock_data("agency_configs", "non_existent_agency", {})

    response = client.get("/v1/api/agency/config?agency_id=non_existent_agency")
    assert response.status_code == 404
    assert response.json() == {"detail": "Agency configuration not found"}
