from unittest.mock import AsyncMock, patch

import pytest

from nalgonda.models.agency_config import AgencyConfig
from nalgonda.models.agent_config import AgentConfig
from tests.test_utils import TEST_USER_ID
from tests.test_utils.constants import TEST_AGENCY_ID


@pytest.mark.usefixtures("mock_get_current_active_user")
def test_get_agency_list_success(client, mock_firestore_client):
    # Setup expected response
    expected_agency = AgencyConfig(agency_id="agency1", owner_id=TEST_USER_ID, name="Test agency")
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, expected_agency.model_dump())

    response = client.get("/v1/api/agency/list")

    assert response.status_code == 200
    assert response.json() == [expected_agency.model_dump()]


@pytest.mark.usefixtures("mock_get_current_active_user")
def test_get_agency_config(client, mock_firestore_client):
    mock_data = {
        "agency_id": TEST_AGENCY_ID,
        "owner_id": TEST_USER_ID,
        "name": "Test agency",
        "shared_instructions": "Test Manifesto",
        "main_agent": None,
        "agents": [],
        "agency_chart": [],
    }
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, mock_data)

    response = client.get("/v1/api/agency?agency_id=test_agency_id")
    assert response.status_code == 200
    assert response.json() == mock_data


@pytest.mark.usefixtures("mock_get_current_active_user")
def test_get_agency_config_not_found(client):
    # Simulate non-existent agency by not setting up any data for it
    response = client.get("/v1/api/agency?agency_id=non_existent_agency")
    assert response.status_code == 404
    assert response.json() == {"detail": "Agency not found"}


@pytest.mark.usefixtures("mock_get_current_active_user")
def test_get_agency_config_owner_id_mismatch(client, mock_firestore_client):
    expected_agency = AgencyConfig(agency_id="agency1", owner_id="different_user_id", name="Test agency")
    mock_firestore_client.setup_mock_data("agency_configs", "agency1", expected_agency.model_dump())

    response = client.get("/v1/api/agency?agency_id=agency1")
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


@pytest.mark.usefixtures("mock_get_current_active_user", "mock_firestore_client")
def test_create_agency_success(client):
    template_config = {
        "agency_id": "template_agency_id",
        "name": "Test agency",
        "shared_instructions": "Manifesto",
        "agents": [],
        "agency_chart": [],
    }

    with patch(
        "nalgonda.services.agency_manager.AgencyManager.update_or_create_agency", new_callable=AsyncMock
    ) as mock_update_or_create_agency:
        mock_update_or_create_agency.return_value = TEST_AGENCY_ID
        response = client.put("/v1/api/agency", json=template_config)

    assert response.status_code == 200
    assert response.json() == {"agency_id": TEST_AGENCY_ID}

    template_config.update({"owner_id": TEST_USER_ID})
    model_template_config = AgencyConfig.model_validate(template_config)
    model_template_config.agency_id = None
    mock_update_or_create_agency.assert_called_once_with(model_template_config)


@pytest.mark.usefixtures("mock_get_current_active_user")
def test_update_agency_success(client, mock_firestore_client):
    # Setup initial data in mock Firestore client
    initial_data = {
        "agency_id": TEST_AGENCY_ID,
        "owner_id": TEST_USER_ID,
        "name": "Test agency",
        "shared_instructions": "Original Manifesto",
        "agents": [],
        "main_agent": None,
        "agency_chart": [],
    }
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, initial_data)
    new_data = initial_data.copy()
    new_data.update({"shared_instructions": "Updated Manifesto"})

    with patch(
        "nalgonda.services.agency_manager.AgencyManager.repopulate_cache_and_update_assistants", new_callable=AsyncMock
    ) as mock_repopulate_cache:
        response = client.put("/v1/api/agency", json=new_data)

    assert response.status_code == 200
    assert response.json() == {"agency_id": initial_data["agency_id"]}

    mock_repopulate_cache.assert_called_once_with(TEST_AGENCY_ID)

    assert mock_firestore_client.to_dict() == new_data


@pytest.mark.usefixtures("mock_get_current_active_user")
def test_update_agency_owner_id_mismatch(client, mock_firestore_client):
    # Setup initial data in mock Firestore client
    initial_data = {
        "agency_id": TEST_AGENCY_ID,
        "owner_id": "some_other_user",
        "name": "Test agency",
        "shared_instructions": "Original Manifesto",
        "agents": [],
        "main_agent": None,
        "agency_chart": [],
    }
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, initial_data)
    new_data = initial_data.copy()
    new_data.update({"shared_instructions": "Updated Manifesto"})

    response = client.put("/v1/api/agency", json=new_data)

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


@pytest.mark.usefixtures("mock_get_current_active_user")
def test_update_agency_with_foreign_agent(client, mock_firestore_client):
    agency_config_data = {
        "agency_id": TEST_AGENCY_ID,
        "owner_id": TEST_USER_ID,
        "name": "Test Agency",
        "agents": ["foreign_agent_id"],
    }
    foreign_agent_config = AgentConfig(
        name="Foreign Agent", owner_id="foreign_owner_id", description="Test Agent", instructions="Test Instructions"
    )
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_config_data)
    mock_firestore_client.setup_mock_data("agent_configs", "foreign_agent_id", foreign_agent_config.model_dump())

    # Simulate a PUT request to update the agency with agents belonging to a different user
    response = client.put("/v1/api/agency", json=agency_config_data)

    # Check if the server responds with a 403 Forbidden
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}

    # Check if the agency config was not updated
    assert mock_firestore_client.collection("agency_configs").to_dict() == agency_config_data


@pytest.mark.usefixtures("mock_get_current_active_user")
def test_update_or_create_agency_missing_agent(client, mock_firestore_client):
    agency_data_with_missing_agent = {
        "agency_id": "existing_agency",
        "name": "Existing Agency with Missing Agent",
        "shared_instructions": "Existing",
        "agents": ["missing_agent_id"],
        "agency_chart": [],
    }

    mock_firestore_client.setup_mock_data("agency_configs", "existing_agency", agency_data_with_missing_agent)
    response = client.put("/v1/api/agency", json=agency_data_with_missing_agent)
    assert response.status_code == 400
    assert response.json() == {"detail": "Agent not found: missing_agent_id"}
