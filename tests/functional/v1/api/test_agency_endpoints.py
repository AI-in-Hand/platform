from unittest.mock import AsyncMock, patch

import pytest

from backend.models.agency_config import AgencyConfig
from backend.models.agent_flow_spec import AgentFlowSpec
from backend.repositories.agent_flow_spec_firestore_storage import AgentFlowSpecFirestoreStorage
from backend.services.adapters.agency_adapter import AgencyConfigAdapter
from tests.test_utils import TEST_USER_ID
from tests.test_utils.constants import TEST_AGENCY_ID


@pytest.fixture
def mock_agent():
    return {
        "id": "sender_agent_id",
        "config": {"name": "Sender Agent"},
    }


@pytest.fixture
@pytest.mark.usefixtures("mock_firestore_client")
def mock_adapter():
    return AgencyConfigAdapter(AgentFlowSpecFirestoreStorage())


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agency_list_success(client, mock_firestore_client, mock_adapter):
    # Setup expected response
    db_agency = AgencyConfig(
        id="agency1",
        user_id=TEST_USER_ID,
        name="Test agency",
        main_agent="Sender Agent",
        agents=["sender_agent_id", "receiver_agent_id"],
        agency_chart=[["Sender Agent", "Receiver Agent"]],
    )
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, db_agency.model_dump())
    mock_firestore_client.setup_mock_data(
        "agent_configs", "sender_agent_id", {"id": "sender_agent_id", "config": {"name": "Sender Agent"}}
    )
    mock_firestore_client.setup_mock_data(
        "agent_configs", "receiver_agent_id", {"id": "receiver_agent_id", "config": {"name": "Receiver Agent"}}
    )
    expected_agency = mock_adapter.to_api(db_agency)

    response = client.get("/v1/api/agency/list")

    assert response.status_code == 200
    assert response.json()["data"] == [expected_agency.model_dump()]


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agency_config(client, mock_firestore_client, mock_adapter):
    db_agency = AgencyConfig(
        id=TEST_AGENCY_ID,
        user_id=TEST_USER_ID,
        name="Test agency",
        description="Test Description",
        shared_instructions="Test Manifesto",
        main_agent="Sender Agent",
        agents=["sender_agent_id"],
    )
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, db_agency)
    mock_firestore_client.setup_mock_data(
        "agent_configs", "sender_agent_id", {"id": "sender_agent_id", "config": {"name": "Sender Agent"}}
    )
    expected_agency = mock_adapter.to_api(db_agency)

    response = client.get("/v1/api/agency?id=test_agency_id")
    assert response.status_code == 200
    assert response.json()["data"] == expected_agency.model_dump()


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agency_config_not_found(client):
    # Simulate non-existent agency by not setting up any data for it
    response = client.get("/v1/api/agency?id=non_existent_agency")
    assert response.status_code == 404
    assert response.json() == {"detail": "Agency not found"}


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agency_config_user_id_mismatch(client, mock_firestore_client):
    expected_agency = AgencyConfig(id="agency1", user_id="different_user_id", name="Test agency")
    mock_firestore_client.setup_mock_data("agency_configs", "agency1", expected_agency.model_dump())

    response = client.get("/v1/api/agency?id=agency1")
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


@pytest.mark.usefixtures("mock_get_current_user", "mock_firestore_client")
def test_create_agency_success(client, mock_agent):
    template_config = {
        "id": "template_agency_id",
        "name": "Test agency",
        "shared_instructions": "Manifesto",
        "sender": mock_agent,
    }

    with patch(
        "backend.services.agency_manager.AgencyManager.update_or_create_agency", new_callable=AsyncMock
    ) as mock_update_or_create_agency:
        mock_update_or_create_agency.return_value = TEST_AGENCY_ID
        response = client.put("/v1/api/agency", json=template_config)

    assert response.status_code == 200
    assert response.json()["data"] == {"agency_id": TEST_AGENCY_ID}

    template_config.update({"user_id": TEST_USER_ID})
    model_template_config = AgencyConfig.model_validate(template_config)
    model_template_config.id = None
    mock_update_or_create_agency.assert_called_once_with(model_template_config)


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_agency_success(client, mock_firestore_client, mock_agent):
    # Setup initial data in mock Firestore client
    initial_data = {
        "id": TEST_AGENCY_ID,
        "user_id": TEST_USER_ID,
        "name": "Test agency",
        "description": "Test Description",
        "shared_instructions": "Original Manifesto",
        "sender": mock_agent,
    }
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, initial_data)
    new_data = initial_data.copy()
    new_data.update({"shared_instructions": "Updated Manifesto"})

    with patch(
        "backend.services.agency_manager.AgencyManager.repopulate_cache_and_update_assistants", new_callable=AsyncMock
    ) as mock_repopulate_cache:
        response = client.put("/v1/api/agency", json=new_data)

    assert response.status_code == 200
    assert response.json()["data"] == {"agency_id": initial_data["id"]}

    mock_repopulate_cache.assert_called_once_with(TEST_AGENCY_ID)

    assert mock_firestore_client.to_dict() == new_data


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_agency_user_id_mismatch(client, mock_firestore_client, mock_agent):
    # Setup initial data in mock Firestore client
    initial_data = {
        "id": TEST_AGENCY_ID,
        "user_id": "some_other_user",
        "name": "Test agency",
        "shared_instructions": "Original Manifesto",
        "sender": mock_agent,
    }
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, initial_data)
    new_data = initial_data.copy()
    new_data.update({"shared_instructions": "Updated Manifesto"})

    response = client.put("/v1/api/agency", json=new_data)

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_agency_with_foreign_agent(client, mock_firestore_client, mock_agent):
    agency_config_data = {
        "id": TEST_AGENCY_ID,
        "user_id": TEST_USER_ID,
        "name": "Test Agency",
        "sender": mock_agent,
    }
    foreign_agent_flow_spec = AgentFlowSpec(
        config={
            "name": "Foreign Agent",
            "system_message": "Test Instructions",
        },
        user_id="foreign_user_id",
    )
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_config_data)
    mock_firestore_client.setup_mock_data("agent_configs", "foreign_agent_id", foreign_agent_flow_spec.model_dump())

    # Simulate a PUT request to update the agency with agents belonging to a different user
    response = client.put("/v1/api/agency", json=agency_config_data)

    # Check if the server responds with a 403 Forbidden
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}

    # Check if the agency config was not updated
    assert mock_firestore_client.collection("agency_configs").to_dict() == agency_config_data


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_or_create_agency_missing_agent(client, mock_firestore_client, mock_agent):
    missing_agent = mock_agent.copy()
    missing_agent["id"] = "missing_agent_id"
    agency_data_with_missing_agent = {
        "id": "existing_agency",
        "name": "Existing Agency with Missing Agent",
        "shared_instructions": "Existing",
        "sender": missing_agent,
    }

    mock_firestore_client.setup_mock_data("agency_configs", "existing_agency", agency_data_with_missing_agent)
    response = client.put("/v1/api/agency", json=agency_data_with_missing_agent)
    assert response.status_code == 400
    assert response.json() == {"detail": "Agent not found: missing_agent_id"}
