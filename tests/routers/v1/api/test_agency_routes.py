from unittest.mock import patch

from nalgonda.models.agency_config import AgencyConfig
from nalgonda.persistence.agency_config_firestore_storage import AgencyConfigFirestoreStorage


@patch.object(
    AgencyConfigFirestoreStorage,
    "load",
    return_value=AgencyConfig(
        agency_id="test_agency",
        owner_id="test_owner",
        agency_manifesto="Test Manifesto",
        agents=[],
        agency_chart=[],
    ),
)
def test_get_agency_config(mock_load, client):  # noqa: ARG001
    response = client.get("/v1/api/agency/config?agency_id=test_agency")
    assert response.status_code == 200
    assert response.json() == {
        "agency_id": "test_agency",
        "owner_id": "test_owner",
        "agency_manifesto": "Test Manifesto",
        "agents": [],
        "agency_chart": [],
    }


test_agency_config = AgencyConfig(
    agency_id="test_agency",
    owner_id="test_owner",
    agency_manifesto="Updated Manifesto",
    agents=[],
    agency_chart=[],
)


@patch.object(AgencyConfigFirestoreStorage, "save")
@patch.object(
    AgencyConfigFirestoreStorage,
    "load",
    return_value=test_agency_config,
)
def test_update_agency_config_success(mock_load, mock_save, client):  # noqa: ARG001
    new_data = {"agency_manifesto": "Updated Manifesto"}
    response = client.put("/v1/api/agency/config?agency_id=test_agency", json=new_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Agency configuration updated successfully"}


@patch.object(AgencyConfigFirestoreStorage, "load", return_value=None)
def test_get_agency_config_not_found(mock_load, client):
    response = client.get("/v1/api/agency/config?agency_id=non_existent_agency")
    assert response.json() == {"detail": "Agency configuration not found"}
    assert response.status_code == 404
    mock_load.assert_called_once()
