from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from agency_swarm import Agency, Agent

from nalgonda.models.agency_config import AgencyConfig
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
    yield AgencyManager(cache_manager=MagicMock(), agent_manager=MagicMock())


@pytest.mark.asyncio
async def test_create_agency_with_new_id(agency_manager):
    # Test creating an agency with a newly generated ID
    with patch(
        "nalgonda.services.agency_manager.AgencyManager.load_and_construct_agents", new_callable=AsyncMock
    ) as mock_load_agents, patch(
        "nalgonda.services.agency_manager.AgencyManager.construct_agency"
    ) as mock_construct_agency, patch(
        "nalgonda.services.agency_manager.AgencyManager.cache_agency", new_callable=AsyncMock
    ) as mock_cache_agency:
        mock_load_agents.return_value = {}
        mock_construct_agency.return_value = MagicMock(spec=Agency)

        new_agency_id = await agency_manager.create_agency(owner_id=TEST_USER_ID)

        assert isinstance(new_agency_id, str)
        mock_load_agents.assert_called_once()
        mock_construct_agency.assert_called_once()
        mock_cache_agency.assert_called_once_with(mock_construct_agency.return_value, new_agency_id, None)


@pytest.mark.asyncio
async def test_create_agency(agency_manager):
    with patch(
        "nalgonda.services.agency_manager.AgencyManager.load_and_construct_agents", new_callable=AsyncMock
    ) as mock_load_agents, patch(
        "nalgonda.services.agency_manager.AgencyManager.construct_agency"
    ) as mock_construct_agency, patch(
        "nalgonda.services.agency_manager.AgencyManager.cache_agency", new_callable=AsyncMock
    ) as mock_cache_agency:
        # Mock return value with necessary agents
        mock_load_agents.return_value = {"agent1": MagicMock(spec=Agent)}
        mock_construct_agency.return_value = MagicMock(spec=Agency)

        agency_id = await agency_manager.create_agency(owner_id=TEST_USER_ID)

        assert isinstance(agency_id, str)
        mock_load_agents.assert_called_once()
        mock_construct_agency.assert_called_once()
        mock_cache_agency.assert_called_once_with(mock_construct_agency.return_value, agency_id, None)


@pytest.mark.asyncio
async def test_get_agency_from_cache(agency_manager):
    with patch.object(agency_manager.cache_manager, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = Agency([], "manifesto")

        agency = await agency_manager.get_agency("test_agency")
        assert agency is not None
        mock_get.assert_called_once_with("test_agency")


@pytest.mark.asyncio
async def test_get_agency_repopulate_cache(agency_manager):
    with patch.object(agency_manager.cache_manager, "get", new_callable=AsyncMock) as mock_get, patch.object(
        agency_manager, "repopulate_cache", new_callable=AsyncMock
    ) as mock_repopulate:
        mock_get.return_value = None
        mock_repopulate.return_value = Agency([], "manifesto")

        agency = await agency_manager.get_agency("test_agency")
        assert agency is not None
        mock_get.assert_called_once_with("test_agency")
        mock_repopulate.assert_called_once_with("test_agency")


@pytest.mark.asyncio
async def test_update_agency(agency_manager):
    agency_config = AgencyConfig(
        agency_id="test_agency",
        owner_id="test_user",
        agency_manifesto="manifesto",
        agents=["agent1_id"],
    )
    updated_data = {"agency_manifesto": "new_manifesto"}

    with patch.object(agency_manager, "repopulate_cache", new_callable=AsyncMock) as mock_repopulate:
        await agency_manager.update_agency(agency_config, updated_data)

        assert agency_config.agency_manifesto == "new_manifesto"
        mock_repopulate.assert_called_once_with("test_agency")


@pytest.mark.asyncio
async def test_repopulate_cache_no_config(agency_manager):
    with patch("nalgonda.services.agency_manager.logger") as mock_logger, patch(
        "asyncio.to_thread", new_callable=AsyncMock
    ) as mock_async_to_thread:
        mock_async_to_thread.return_value = None

        result = await agency_manager.repopulate_cache("nonexistent_agency_id")
        assert result is None
        mock_async_to_thread.assert_called_once()
        mock_logger.error.assert_called_once_with("Agency with id nonexistent_agency_id not found.")


@pytest.mark.asyncio
async def test_repopulate_cache_success(agency_manager, mock_firestore_client):
    agency_config = AgencyConfig(
        agency_id="test_agency",
        owner_id="test_user",
        agency_manifesto="manifesto",
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

        result = await agency_manager.repopulate_cache("test_agency")
        assert result is not None
        mock_load_agents.assert_called_once_with(agency_config)
        mock_construct_agency.assert_called_once_with(agency_config, {"agent1": agent})
        mock_cache_agency.assert_called_once_with(mock_construct_agency.return_value, "test_agency", None)


# Test successful agent construction
@pytest.mark.asyncio
async def test_load_and_construct_agents_success():
    agency_config = AgencyConfig(
        agency_id="test_agency",
        owner_id="test_user",
        agency_manifesto="Test manifesto",
        agents=["agent1_id"],
    )
    agent_config_mock = Mock()
    agent_config_mock.name = "agent1_name"
    agent_mock = MagicMock(spec=Agent)
    agent_mock.id = "agent1_id"

    agent_manager_mock = AsyncMock()
    agent_manager_mock.get_agent.return_value = (agent_mock, agent_config_mock)

    agency_manager = AgencyManager(cache_manager=MagicMock(), agent_manager=agent_manager_mock)
    agents = await agency_manager.load_and_construct_agents(agency_config)

    assert "agent1_name" in agents
    assert isinstance(agents["agent1_name"], Agent)
    assert agents["agent1_name"].id == "agent1_id"


# Test agent not found
@pytest.mark.asyncio
async def test_load_and_construct_agents_agent_not_found():
    agency_config = AgencyConfig(
        agency_id="test_agency",
        owner_id="test_user",
        agency_manifesto="Test manifesto",
        agents=["agent1_id"],
    )

    agent_manager_mock = AsyncMock()
    agent_manager_mock.get_agent.return_value = None

    with patch("logging.Logger.error") as mock_logger_error:
        agency_manager = AgencyManager(cache_manager=MagicMock(), agent_manager=agent_manager_mock)
        agents = await agency_manager.load_and_construct_agents(agency_config)

        assert agents == {}
        mock_logger_error.assert_called_with("Agent with id agent1_id not found.")


@pytest.mark.asyncio
async def test_construct_agency_single_layer_chart():
    # Mock AgencyConfig
    agency_config = AgencyConfig(
        agency_id="test_agency",
        owner_id="test_user",
        agency_manifesto="manifesto",
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

    # AgencyManager instance
    agency_manager = AgencyManager(cache_manager=MagicMock(), agent_manager=MagicMock())

    # Construct the agency
    agency = agency_manager.construct_agency(agency_config, {"agent1_name": mock_agent_1, "agent2_name": mock_agent_2})

    # Assertions
    assert isinstance(agency, Agency)
    assert len(agency.agents) == 2
    assert agency.agents == [mock_agent_1, mock_agent_2]
    assert agency.shared_instructions == "manifesto"
