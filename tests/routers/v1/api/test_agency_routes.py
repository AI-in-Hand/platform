from unittest.mock import patch

from fastapi.testclient import TestClient

from nalgonda.main import app
from nalgonda.models.agency_config import AgencyConfig


def get_mocked_agency_config(agency_id: str):
    # This is a stub for generating a mocked AgencyConfig instance
    return AgencyConfig(agency_id=agency_id, agency_manifesto="Mocked Agency Manifesto")


@patch("persistence.agency_config_firestore_storage.AgencyConfigFirestoreStorage.load")
@patch("persistence.agency_config_firestore_storage.AgencyConfigFirestoreStorage.save")
def test_get_agency_config(mock_load, mock_save):
    # Configure the mock to return a mocked AgencyConfig upon load
    mock_load.return_value = {"agency_id": "test_agency", "agency_manifesto": "Mocked Agency Manifesto"}
    client = TestClient(app)

    # Send a GET request to the /agency/config endpoint
    response = client.get("/agency/config?agency_id=test_agency")
    assert response.status_code == 200
    assert response.json() == {"agency_id": "test_agency", "agency_manifesto": "Mocked Agency Manifesto"}

    # Test updating agency_config through a POST request and ensure correct saving
    new_data = {"agency_manifesto": "Updated Manifesto"}
    response = client.post("/agency/config?agency_id=test_agency", json=new_data)
    assert response.status_code == 201
    assert response.json() == {"message": "Config updated successfully"}
    mock_save.assert_called_with(new_data)
