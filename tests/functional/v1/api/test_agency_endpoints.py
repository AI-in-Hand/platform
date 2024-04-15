from unittest import mock
from unittest.mock import AsyncMock, patch

import pytest

from backend.models.agency_config import AgencyConfig, AgencyConfigForAPI
from backend.models.agent_flow_spec import AgentFlowSpec
from backend.repositories.agent_flow_spec_storage import AgentFlowSpecStorage
from backend.repositories.skill_config_storage import SkillConfigStorage
from backend.services.adapters.agency_adapter import AgencyAdapter
from backend.services.adapters.agent_adapter import AgentAdapter
from tests.testing_utils import TEST_USER_ID
from tests.testing_utils.constants import TEST_AGENCY_ID


@pytest.fixture
def mock_agent():
    return {
        "id": "sender_agent_id",
        "type": "userproxy",
        "config": {
            "name": "Sender Agent",
            "system_message": "Do something important.",
            "code_execution_config": {
                "work_dir": None,
                "use_docker": False,
            },
        },
        "timestamp": "2024-04-04T09:39:13.048457+00:00",
        "skills": [],
        "description": "An example agent.",
        "user_id": TEST_USER_ID,
    }


@pytest.fixture
@pytest.mark.usefixtures("mock_firestore_client")
def agency_adapter():
    return AgencyAdapter(AgentFlowSpecStorage(), AgentAdapter(SkillConfigStorage()))


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agency_list_success(client, mock_firestore_client, agency_adapter):
    # Setup expected response
    db_agency = AgencyConfig(
        id="agency1",
        user_id=TEST_USER_ID,
        name="Test agency",
        main_agent="Sender Agent",
        agents=["sender_agent_id", "receiver_agent_id"],
        agency_chart={0: ["Sender Agent", "Receiver Agent"]},
    )
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, db_agency.model_dump())
    mock_firestore_client.setup_mock_data(
        "agent_configs", "sender_agent_id", {"id": "sender_agent_id", "config": {"name": "Sender Agent"}}
    )
    mock_firestore_client.setup_mock_data(
        "agent_configs", "receiver_agent_id", {"id": "receiver_agent_id", "config": {"name": "Receiver Agent"}}
    )
    expected_agency = agency_adapter.to_api(db_agency)

    response = client.get("/api/v1/agency/list")

    assert response.status_code == 200
    assert response.json()["data"] == [expected_agency.model_dump()]


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agency_config(client, mock_firestore_client, agency_adapter):
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
    expected_agency = agency_adapter.to_api(db_agency)

    response = client.get("/api/v1/agency?id=test_agency_id")
    assert response.status_code == 200
    assert response.json()["data"] == expected_agency.model_dump()


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agency_config_not_found(client):
    # Simulate non-existent agency by not setting up any data for it
    response = client.get("/api/v1/agency?id=non_existent_agency")
    assert response.status_code == 404
    assert response.json() == {"detail": "Agency not found"}


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agency_config_user_id_mismatch(client, mock_firestore_client):
    expected_agency = AgencyConfig(id="agency1", user_id="different_user_id", name="Test agency")
    mock_firestore_client.setup_mock_data("agency_configs", "agency1", expected_agency.model_dump())

    response = client.get("/api/v1/agency?id=agency1")
    assert response.status_code == 403
    assert response.json() == {"detail": "You don't have permissions to access this agency"}


@pytest.mark.usefixtures("mock_get_current_user")
def test_create_agency_success(client, mock_agent, agency_adapter, mock_firestore_client):
    template_config = {
        "id": "template_agency_id",
        "name": "Test agency",
        "shared_instructions": "Manifesto",
        "sender": mock_agent,
    }
    mock_firestore_client.setup_mock_data("agent_configs", "sender_agent_id", mock_agent)
    with patch(
        "backend.services.agency_manager.AgencyManager.handle_agency_creation_or_update", new_callable=AsyncMock
    ) as mock_update_or_create_agency:
        mock_update_or_create_agency.return_value = TEST_AGENCY_ID
        response = client.put("/api/v1/agency", json=template_config)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)  # TODO: check the response data more thoroughly
    model_template_config = agency_adapter.to_model(AgencyConfigForAPI(**template_config))
    mock_update_or_create_agency.assert_called_once_with(model_template_config, TEST_USER_ID)


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_agency_success(client, mock_firestore_client, mock_agent, agency_adapter):
    # Setup initial data in mock Firestore client
    initial_db_data = {
        "id": TEST_AGENCY_ID,
        "user_id": TEST_USER_ID,
        "name": "Test agency",
        "description": "Test Description",
        "shared_instructions": "Original Manifesto",
        "agents": ["sender_agent_id"],
        "main_agent": "Sender Agent",
    }
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, initial_db_data)
    mock_firestore_client.setup_mock_data("agent_configs", "sender_agent_id", mock_agent)
    new_data_payload = {
        "id": TEST_AGENCY_ID,
        "name": "Test agency",
        "description": "Test Description",
        "shared_instructions": "Updated Manifesto",
        "sender": mock_agent,
        "receiver": None,
        "user_id": TEST_USER_ID,
        "timestamp": "2024-04-04T09:39:13.048457+00:00",
    }
    expected_data_from_api = new_data_payload.copy()
    expected_data_from_api["timestamp"] = mock.ANY
    with patch(
        "backend.services.agency_manager.AgencyManager.repopulate_cache_and_update_assistants", new_callable=AsyncMock
    ) as mock_repopulate_cache:
        response = client.put("/api/v1/agency", json=new_data_payload)

    assert response.status_code == 200
    assert response.json()["data"] == [expected_data_from_api]
    mock_repopulate_cache.assert_called_once_with(TEST_AGENCY_ID)
    expected_data = agency_adapter.to_model(AgencyConfigForAPI(**new_data_payload)).model_dump()
    expected_data["timestamp"] = mock.ANY
    assert mock_firestore_client.collection("agency_configs").to_dict() == expected_data


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

    response = client.put("/api/v1/agency", json=new_data)

    assert response.status_code == 403
    assert response.json() == {"detail": "You don't have permissions to update this agency"}


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_agency_with_foreign_agent(client, mock_firestore_client, agency_adapter):
    db_agency = {
        "id": TEST_AGENCY_ID,
        "user_id": TEST_USER_ID,
        "name": "Test Agency",
        "agents": ["sender_agent_id", "foreign_agent_id"],
        "main_agent": "Sender Agent",
    }
    foreign_agent_flow_spec = AgentFlowSpec(
        config={"name": "Foreign Agent"},
        user_id="foreign_user_id",
    )
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, db_agency)
    mock_firestore_client.setup_mock_data(
        "agent_configs", "sender_agent_id", {"id": "sender_agent_id", "config": {"name": "Sender Agent"}}
    )
    mock_firestore_client.setup_mock_data("agent_configs", "foreign_agent_id", foreign_agent_flow_spec.model_dump())
    # Simulate a PUT request to update the agency with agents belonging to a different user
    new_data = agency_adapter.to_api(AgencyConfig(**db_agency)).model_dump()
    response = client.put("/api/v1/agency", json=new_data)
    # Check if the server responds with a 403 Forbidden
    assert response.status_code == 403
    assert response.json() == {"detail": "You don't have permissions to use agent sender_agent_id"}
    # Check if the agency config was not updated
    assert mock_firestore_client.collection("agency_configs").to_dict() == db_agency


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
    response = client.put("/api/v1/agency", json=agency_data_with_missing_agent)
    assert response.status_code == 400
    assert response.json() == {"detail": "Agent not found: missing_agent_id"}


@pytest.mark.usefixtures("mock_get_current_user")
def test_delete_agency_success(client, mock_firestore_client):
    db_agency = {
        "id": TEST_AGENCY_ID,
        "user_id": TEST_USER_ID,
        "name": "Test Agency",
    }
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, db_agency)

    with patch(
        "backend.services.agency_manager.AgencyManager.delete_agency_from_cache", new_callable=AsyncMock
    ) as mock_delete_agency_from_cache:
        response = client.delete(f"/api/v1/agency?id={TEST_AGENCY_ID}")
    assert response.status_code == 200
    assert response.json() == {"status": True, "message": "Agency deleted", "data": []}
    assert mock_firestore_client.collection("agency_configs").to_dict() == {}
    mock_delete_agency_from_cache.assert_called_once_with(TEST_AGENCY_ID, None)


@pytest.mark.usefixtures("mock_get_current_user")
def test_delete_agency_not_found(client):
    response = client.delete("/api/v1/agency?id=non_existent_agency")
    assert response.status_code == 404
    assert response.json() == {"detail": "Agency not found"}


@pytest.mark.usefixtures("mock_get_current_user")
def test_delete_agency_user_id_mismatch(client, mock_firestore_client):
    db_agency = {
        "id": TEST_AGENCY_ID,
        "user_id": "some_other_user",
        "name": "Test Agency",
    }
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, db_agency)

    response = client.delete(f"/api/v1/agency?id={TEST_AGENCY_ID}")
    assert response.status_code == 403
    assert response.json() == {"detail": "You don't have permissions to delete this agency"}
