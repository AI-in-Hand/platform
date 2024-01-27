from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from agency_swarm import Agency, Agent

from nalgonda.models.agency_config import AgencyConfig
from nalgonda.persistence.agency_config_firestore_storage import AgencyConfigFirestoreStorage
from nalgonda.services.agency_manager import AgencyManager
from tests.test_utils import TEST_USER_ID


class MockRedisCacheManager:
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):  # noqa: ARG001, ARG002
        return self

    async def get(self, key):  # noqa: ARG002
        return None

    async def set(self, key, value):
        pass

    async def delete(self, key):
        pass


@pytest.fixture
def agency_manager(mock_firestore_client):  # noqa: ARG001
    yield AgencyManager(
        cache_manager=MagicMock(), agent_manager=MagicMock(), agency_config_storage=AgencyConfigFirestoreStorage()
    )


@pytest.mark.asyncio
async def test_get_agency_from_cache(agency_manager):
    with patch.object(agency_manager.cache_manager, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = Agency([], "manifesto")

        agency = await agency_manager.get_agency("test_agency_id")
        assert agency is not None
        mock_get.assert_called_once_with("test_agency_id")


@pytest.mark.asyncio
async def test_get_agency_repopulate_cache(agency_manager):
    with patch.object(agency_manager.cache_manager, "get", new_callable=AsyncMock) as mock_get, patch.object(
        agency_manager, "repopulate_cache_and_update_assistants", new_callable=AsyncMock
    ) as mock_repopulate:
        mock_get.return_value = None
        mock_repopulate.return_value = Agency([], "manifesto")

        agency = await agency_manager.get_agency("test_agency_id")
        assert agency is not None
        mock_get.assert_called_once_with("test_agency_id")
        mock_repopulate.assert_called_once_with("test_agency_id")


@pytest.mark.asyncio
async def test_update_or_create_agency(agency_manager, mock_firestore_client):
    agency_config = AgencyConfig(
        agency_id="test_agency_id",
        owner_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="Initial manifesto",
        agents=["agent1_id"],
    )
    mock_firestore_client.setup_mock_data("agency_configs", "test_agency_id", agency_config.model_dump())
    agency_config.shared_instructions = "New manifesto"

    with patch.object(
        agency_manager, "repopulate_cache_and_update_assistants", new_callable=AsyncMock
    ) as mock_repopulate:
        agency_id = await agency_manager.update_or_create_agency(agency_config)

    mock_repopulate.assert_called_once_with("test_agency_id")
    assert agency_id == "test_agency_id"
    assert mock_firestore_client.to_dict()["shared_instructions"] == "New manifesto"


@pytest.mark.asyncio
async def test_repopulate_cache_no_config(agency_manager):
    with patch("nalgonda.services.agency_manager.logger") as mock_logger, patch(
        "asyncio.to_thread", new_callable=AsyncMock
    ) as mock_async_to_thread:
        mock_async_to_thread.return_value = None

        result = await agency_manager.repopulate_cache_and_update_assistants("nonexistent_agency_id")
        assert result is None
        mock_async_to_thread.assert_called_once()
        mock_logger.error.assert_called_once_with("Agency with id nonexistent_agency_id not found.")


@pytest.mark.asyncio
async def test_repopulate_cache_success(agency_manager, mock_firestore_client):
    agency_config = AgencyConfig(
        agency_id="test_agency_id",
        owner_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="manifesto",
        agents=["agent1_id"],
    )
    agent = MagicMock(spec=Agent)

    with patch(
        "nalgonda.services.agency_manager.AgencyManager.load_and_construct_agents", new_callable=AsyncMock
    ) as mock_load_agents, patch(
        "nalgonda.services.agency_manager.AgencyManager.construct_agency"
    ) as mock_construct_agency, patch(
        "nalgonda.services.agency_manager.AgencyManager.cache_agency", new_callable=AsyncMock
    ) as mock_cache_agency:
        mock_firestore_client.setup_mock_data("agency_configs", agency_config.agency_id, agency_config)
        mock_load_agents.return_value = {"agent1": agent}
        mock_construct_agency.return_value = Agency([], "manifesto")

        result = await agency_manager.repopulate_cache_and_update_assistants("test_agency_id")
        assert result is not None
        mock_load_agents.assert_called_once_with(agency_config)
        mock_construct_agency.assert_called_once_with(agency_config, {"agent1": agent})
        mock_cache_agency.assert_called_once_with(mock_construct_agency.return_value, "test_agency_id", None)


# Test successful agent construction
@pytest.mark.asyncio
async def test_load_and_construct_agents_success(agency_manager):
    agency_config = AgencyConfig(
        agency_id="test_agency_id",
        owner_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="Test manifesto",
        agents=["agent1_id"],
    )
    agent_config_mock = Mock()
    agent_config_mock.name = "agent1_name"
    agent_mock = MagicMock(spec=Agent)
    agent_mock.id = "agent1_id"

    agent_manager_mock = AsyncMock()
    agent_manager_mock.get_agent.return_value = (agent_mock, agent_config_mock)

    agency_manager.agent_manager = agent_manager_mock

    agents = await agency_manager.load_and_construct_agents(agency_config)

    assert "agent1_name" in agents
    assert isinstance(agents["agent1_name"], Agent)
    assert agents["agent1_name"].id == "agent1_id"


# Test agent not found
@pytest.mark.asyncio
async def test_load_and_construct_agents_agent_not_found(agency_manager):
    agency_config = AgencyConfig(
        agency_id="test_agency_id",
        owner_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="Test manifesto",
        agents=["agent1_id"],
    )

    agent_manager_mock = AsyncMock()
    agent_manager_mock.get_agent.return_value = None
    agency_manager.agent_manager = agent_manager_mock

    with patch("logging.Logger.error") as mock_logger_error:
        agents = await agency_manager.load_and_construct_agents(agency_config)

        assert agents == {}
        mock_logger_error.assert_called_with("Agent with id agent1_id not found.")


@pytest.mark.asyncio
async def test_construct_agency_single_layer_chart(agency_manager):
    # Mock AgencyConfig
    agency_config = AgencyConfig(
        agency_id="test_agency_id",
        owner_id=TEST_USER_ID,
        name="Test agency",
        shared_instructions="manifesto",
        agents=["agent1_id", "agent2_id"],
        main_agent="agent1_name",
        agency_chart=[["agent1_name", "agent2_name"]],
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
    agency = agency_manager.construct_agency(agency_config, {"agent1_name": mock_agent_1, "agent2_name": mock_agent_2})

    # Assertions
    assert isinstance(agency, Agency)
    assert len(agency.agents) == 2
    assert agency.agents == [mock_agent_1, mock_agent_2]
    assert agency.shared_instructions == "manifesto"
