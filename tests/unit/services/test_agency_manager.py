from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from agency_swarm import Agency, Agent

from backend.dependencies.dependencies import get_user_secret_manager
from backend.models.agency_config import AgencyConfig
from backend.repositories.agency_config_storage import AgencyConfigStorage
from backend.repositories.user_secret_storage import UserSecretStorage
from backend.services.agency_manager import AgencyManager
from tests.testing_utils import TEST_USER_ID
from tests.testing_utils.constants import TEST_AGENCY_ID


@pytest.fixture
@pytest.mark.usefixtures("mock_firestore_client")
def agency_manager():
    yield AgencyManager(
        agent_manager=MagicMock(),
        agency_config_storage=AgencyConfigStorage(),
        user_secret_manager=get_user_secret_manager(user_secret_storage=UserSecretStorage()),
    )


# test get_agency_list method
@pytest.mark.asyncio
async def test_get_agency_list(agency_manager, mock_firestore_client):
    agency_config = AgencyConfig(
        id=TEST_AGENCY_ID,
        user_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="manifesto",
        main_agent="agent1_name",
        agents=["agent1_id"],
    )
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_config.model_dump())

    agency_list = await agency_manager.get_agency_list(TEST_USER_ID)
    assert len(agency_list) == 1
    assert agency_list[0] == agency_config


@pytest.mark.asyncio
async def test_get_agency_construct_agency(agency_manager, mock_firestore_client):
    agency_config_dict = {"name": "Test agency", "id": TEST_AGENCY_ID}
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_config_dict)
    with patch.object(
        agency_manager, "_construct_agency_and_update_assistants", new_callable=AsyncMock
    ) as mock_construct:
        mock_construct.return_value = MagicMock(spec=Agency)
        agency = await agency_manager.get_agency(TEST_AGENCY_ID, {})
        assert agency is not None
        mock_construct.assert_called_once_with(AgencyConfig(**agency_config_dict), {})


@pytest.mark.asyncio
async def test_create_or_update_agency(agency_manager, mock_firestore_client):
    agency_config = AgencyConfig(
        id=TEST_AGENCY_ID,
        user_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="Initial manifesto",
        main_agent="agent1_name",
        agents=["agent1_id"],
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
        main_agent="agent1_name",
        agents=["agent1_id"],
    )
    agent_flow_spec_mock = Mock()
    agent_flow_spec_mock.config.name = "agent1_name"
    agent_mock = MagicMock(spec=Agent)
    agent_mock.id = "agent1_id"

    agent_manager_mock = AsyncMock()
    agent_manager_mock.get_agent.return_value = (agent_mock, agent_flow_spec_mock)

    agency_manager.agent_manager = agent_manager_mock

    agents = await agency_manager._load_and_construct_agents(agency_config)

    assert "agent1_name" in agents
    assert isinstance(agents["agent1_name"], Agent)
    assert agents["agent1_name"].id == "agent1_id"


# Test agent not found
@pytest.mark.asyncio
async def test_load_and_construct_agents_agent_not_found(agency_manager):
    agency_config = AgencyConfig(
        id=TEST_AGENCY_ID,
        user_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="Test manifesto",
        main_agent="agent1_name",
        agents=["agent1_id"],
    )

    agent_manager_mock = AsyncMock()
    agent_manager_mock.get_agent.return_value = None
    agency_manager.agent_manager = agent_manager_mock

    with patch("logging.Logger.error") as mock_logger_error:
        agents = await agency_manager._load_and_construct_agents(agency_config)

        assert agents == {}
        mock_logger_error.assert_called_with("Agent with id agent1_id not found.")


@pytest.mark.asyncio
async def test_construct_agency_single_layer_chart(agency_manager):
    # Mock AgencyConfig
    agency_config = AgencyConfig(
        id=TEST_AGENCY_ID,
        user_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="manifesto",
        agents=["agent1_id", "agent2_id"],
        main_agent="agent1_name",
        agency_chart={"0": ["agent1_name", "agent2_name"]},
    )

    # Mock agents
    mock_agent_1 = MagicMock(spec=Agent)
    mock_agent_1.id = "agent1_id"
    mock_agent_1.name = "agent1_name"
    mock_agent_1.description = "agent1_description"
    mock_agent_2 = MagicMock(spec=Agent)
    mock_agent_2.id = "agent2_id"
    mock_agent_2.name = "agent2_name"
    mock_agent_2.description = "agent2_description"

    # Construct the agency
    with patch.object(agency_manager, "_load_and_construct_agents", new_callable=AsyncMock) as mock_load_agents:
        mock_load_agents.return_value = {"agent1_name": mock_agent_1, "agent2_name": mock_agent_2}
        agency = await agency_manager._construct_agency_and_update_assistants(agency_config, {})

    # Assertions
    assert isinstance(agency, Agency)
    assert len(agency.agents) == 2
    assert agency.agents == [mock_agent_1, mock_agent_2]
    assert agency.shared_instructions == "manifesto"


@pytest.mark.asyncio
async def test_delete_agency(agency_manager, mock_firestore_client):
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, {"id": TEST_AGENCY_ID})
    await agency_manager.delete_agency(TEST_AGENCY_ID)
    assert mock_firestore_client.to_dict() == {}
