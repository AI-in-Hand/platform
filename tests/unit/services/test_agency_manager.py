from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from agency_swarm import Agency, Agent
from fastapi import HTTPException

from backend.dependencies.dependencies import get_user_variable_manager
from backend.models.agency_config import AgencyConfig
from backend.repositories.agency_config_storage import AgencyConfigStorage
from backend.repositories.user_variable_storage import UserVariableStorage
from backend.services.agency_manager import AgencyManager, agency_cache
from tests.testing_utils import TEST_USER_ID
from tests.testing_utils.constants import TEST_AGENCY_ID, TEST_AGENT_ID


@pytest.fixture
@pytest.mark.usefixtures("mock_firestore_client")
def agency_manager():
    yield AgencyManager(
        agent_manager=MagicMock(),
        agency_config_storage=AgencyConfigStorage(),
        user_variable_manager=get_user_variable_manager(user_variable_storage=UserVariableStorage()),
    )


# test get_agency_list method
@pytest.mark.asyncio
async def test_get_agency_list(agency_manager, mock_firestore_client):
    agency_config = AgencyConfig(
        id=TEST_AGENCY_ID,
        user_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="manifesto",
        main_agent="Sender Agent",
        agents=[TEST_AGENT_ID],
    )
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_config.model_dump())

    agency_list = await agency_manager.get_agency_list(TEST_USER_ID)
    assert len(agency_list) == 1
    assert agency_list[0] == agency_config


@pytest.mark.asyncio
async def test_get_agency_construct_agency(agency_manager, mock_firestore_client):
    agency_config_dict = {
        "name": "Test agency",
        "id": TEST_AGENCY_ID,
        "user_id": TEST_USER_ID,
        "main_agent": "Sender Agent",
        "agents": [TEST_AGENT_ID],
        "timestamp": "2024-05-05T00:14:57.487901+00:00",
    }
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_config_dict)
    with patch.object(
        agency_manager, "_construct_agency_and_update_assistants", new_callable=AsyncMock
    ) as mock_construct:
        mock_construct.return_value = MagicMock(spec=Agency)
        agency, _ = await agency_manager.get_agency(TEST_AGENCY_ID, {}, TEST_USER_ID)
        assert agency is not None
        mock_construct.assert_called_once_with(AgencyConfig(**agency_config_dict), {})


@pytest.mark.asyncio
async def test_create_or_update_agency(agency_manager, mock_firestore_client):
    agency_config = AgencyConfig(
        id=TEST_AGENCY_ID,
        user_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="Initial manifesto",
        main_agent="Sender Agent",
        agents=[TEST_AGENT_ID],
    )
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_config.model_dump())
    agency_config.shared_instructions = "New manifesto"

    id_ = await agency_manager._create_or_update_agency(agency_config)

    assert id_ == TEST_AGENCY_ID
    assert mock_firestore_client.to_dict()["shared_instructions"] == "New manifesto"


# Test successful agent construction
@pytest.mark.asyncio
async def test_load_and_construct_agents_success(agency_manager):
    agency_config = AgencyConfig(
        id=TEST_AGENCY_ID,
        user_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="Test manifesto",
        main_agent="Sender Agent",
        agents=[TEST_AGENT_ID],
    )
    agent_flow_spec_mock = Mock()
    agent_flow_spec_mock.config.name = "Sender Agent"
    agent_mock = MagicMock(spec=Agent)
    agent_mock.id = TEST_AGENT_ID

    agent_manager_mock = AsyncMock()
    agent_manager_mock.get_agent.return_value = (agent_mock, agent_flow_spec_mock)

    agency_manager.agent_manager = agent_manager_mock

    agents = await agency_manager._load_and_construct_agents(agency_config)

    assert "Sender Agent" in agents
    assert isinstance(agents["Sender Agent"], Agent)
    assert agents["Sender Agent"].id == TEST_AGENT_ID


# Test agent not found
@pytest.mark.asyncio
async def test_load_and_construct_agents_agent_not_found(agency_manager):
    agency_config = AgencyConfig(
        id=TEST_AGENCY_ID,
        user_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="Test manifesto",
        main_agent="Sender Agent",
        agents=[TEST_AGENT_ID],
    )

    agent_manager_mock = AsyncMock()
    agent_manager_mock.get_agent.return_value = None
    agency_manager.agent_manager = agent_manager_mock

    with patch("logging.Logger.error") as mock_logger_error:
        agents = await agency_manager._load_and_construct_agents(agency_config)

        assert agents == {}
        mock_logger_error.assert_called_with("Agent with id sender_agent_id not found.")


@pytest.mark.asyncio
async def test_construct_agency_single_layer_chart(agency_manager):
    # Mock AgencyConfig
    agency_config = AgencyConfig(
        id=TEST_AGENCY_ID,
        user_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="manifesto",
        agents=[TEST_AGENT_ID, "agent2_id"],
        main_agent="Sender Agent",
        agency_chart={"0": ["Sender Agent", "agent2_name"]},
        timestamp="2024-05-05T00:14:57.487901+00:00",
    )

    # Mock agents
    mock_agent_1 = MagicMock(spec=Agent)
    mock_agent_1.id = TEST_AGENT_ID
    mock_agent_1.name = "Sender Agent"
    mock_agent_1.description = "agent1_description"
    mock_agent_1.temperature = 0.5
    mock_agent_1.top_p = 1.0
    mock_agent_1.examples = []
    mock_agent_2 = MagicMock(spec=Agent)
    mock_agent_2.id = "agent2_id"
    mock_agent_2.name = "agent2_name"
    mock_agent_2.description = "agent2_description"
    mock_agent_2.temperature = 0.5
    mock_agent_2.top_p = 1.0
    mock_agent_2.examples = []

    # Clear the agency cache before the test
    agency_cache.clear()

    # Construct the agency
    with patch.object(agency_manager, "_load_and_construct_agents", new_callable=AsyncMock) as mock_load_agents:
        mock_load_agents.return_value = {"Sender Agent": mock_agent_1, "agent2_name": mock_agent_2}
        agency = await agency_manager._construct_agency_and_update_assistants(agency_config, {})

    # Assertions
    assert isinstance(agency, Agency)
    assert len(agency.agents) == 2
    assert agency.agents == [mock_agent_1, mock_agent_2]
    assert agency.shared_instructions == "manifesto"

    # Verify that the agency is cached
    cache_key = "8147cad3c67ff29b97a59e6e1fc1ae9ddc4e6738c2d41190516480a916d0c40e"
    assert cache_key in agency_cache
    assert agency_cache[cache_key] == agency

    # Call the method again with the same arguments
    with patch.object(agency_manager, "_load_and_construct_agents", new_callable=AsyncMock) as mock_load_agents:
        mock_load_agents.return_value = {"Sender Agent": mock_agent_1, "agent2_name": mock_agent_2}
        cached_agency = await agency_manager._construct_agency_and_update_assistants(agency_config, {})

    # Verify that the cached agency is returned
    assert cached_agency == agency
    assert mock_load_agents.call_count == 0  # Ensure that _load_and_construct_agents is not called again


@pytest.mark.asyncio
async def test_delete_agency(agency_manager, mock_firestore_client):
    mock_firestore_client.setup_mock_data(
        "agency_configs",
        TEST_AGENCY_ID,
        {"id": TEST_AGENCY_ID, "name": "Test Agency", "main_agent": "Test Agent", "user_id": TEST_USER_ID},
    )
    await agency_manager.delete_agency(TEST_AGENCY_ID, current_user_id=TEST_USER_ID)
    assert mock_firestore_client.to_dict() == {}


def test_validate_agency_ownership_success(agency_manager):
    agency_manager.validate_agency_ownership("user_id", "user_id")


def test_validate_agency_ownership_raises_403(agency_manager):
    with pytest.raises(HTTPException) as exc_info:
        agency_manager.validate_agency_ownership("another_user_id", "user_id")
    assert exc_info.value.status_code == HTTPStatus.FORBIDDEN


def test_is_agent_used_in_agencies(agency_manager, mock_firestore_client):
    agency_config = AgencyConfig(
        id=TEST_AGENCY_ID,
        user_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="manifesto",
        main_agent="Sender Agent",
        agents=[TEST_AGENT_ID],
    )
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_config.model_dump())
    assert agency_manager.is_agent_used_in_agencies(TEST_AGENT_ID)
    assert not agency_manager.is_agent_used_in_agencies("another_agent_id")
