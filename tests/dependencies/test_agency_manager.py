from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from agency_swarm import Agency, Agent

from nalgonda.dependencies.agency_manager import AgencyManager
from nalgonda.models.agency_config import AgencyConfig


# Mock classes
class MockAgencyConfigFirestoreStorage:
    def load_or_create(self):
        return AgencyConfig(
            agency_id="test_agency",
            owner_id="test_owner_id",
            agents=["agent1"],
            agency_chart=["agent1"],
            agency_manifesto="manifesto",
        )

    def load(self):
        return AgencyConfig(
            agency_id="test_agency",
            owner_id="test_owner_id",
            agents=["agent1"],
            agency_chart=["agent1"],
            agency_manifesto="manifesto",
        )

    def save(self, agency_config):
        pass


class MockAgentConfigFirestoreStorage:
    def load(self, agent_id):
        return MagicMock(
            agent_id=agent_id,
            role="role1",
            description="desc",
            instructions="instr",
            tools=["tool1"],
        )

    def save(self, agent_config):
        pass


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
def agency_manager():
    with patch("nalgonda.dependencies.agency_manager.AgencyConfigFirestoreStorage") as mock_storage_class, patch(
        "nalgonda.dependencies.agency_manager.AgentConfigFirestoreStorage"
    ) as mock_agent_storage_class, patch(
        "nalgonda.dependencies.agency_manager.RedisCacheManager", MockRedisCacheManager()
    ):
        mock_storage_instance = MockAgencyConfigFirestoreStorage()
        mock_storage_class.return_value = mock_storage_instance

        mock_agent_storage_instance = MockAgentConfigFirestoreStorage()
        mock_agent_storage_class.return_value = mock_agent_storage_instance

        yield AgencyManager(redis=MagicMock())


@pytest.fixture(autouse=True)
def mock_tool_mapping():
    with patch("nalgonda.dependencies.agency_manager.TOOL_MAPPING", {"tool1": MagicMock()}):
        yield


@pytest.mark.asyncio
async def test_create_agency_with_new_id(agency_manager):
    # Test creating an agency with a newly generated ID
    with patch(
        "nalgonda.dependencies.agency_manager.AgencyManager.load_and_construct_agents", new_callable=AsyncMock
    ) as mock_load_agents, patch(
        "nalgonda.dependencies.agency_manager.AgencyManager.construct_agency"
    ) as mock_construct_agency, patch(
        "nalgonda.dependencies.agency_manager.AgencyManager.cache_agency", new_callable=AsyncMock
    ):
        mock_load_agents.return_value = {}
        mock_construct_agency.return_value = MagicMock(spec=Agency)

        agency, new_agency_id = await agency_manager.create_agency()

        assert agency is not None
        assert isinstance(new_agency_id, str)
        mock_load_agents.assert_called_once()
        mock_construct_agency.assert_called_once()


@pytest.mark.asyncio
async def test_create_agency_with_provided_id(agency_manager):
    # Test creating an agency with a provided ID
    provided_id = "test_id"
    with patch(
        "nalgonda.dependencies.agency_manager.AgencyManager.load_and_construct_agents", new_callable=AsyncMock
    ) as mock_load_agents, patch(
        "nalgonda.dependencies.agency_manager.AgencyManager.construct_agency"
    ) as mock_construct_agency, patch(
        "nalgonda.dependencies.agency_manager.AgencyManager.cache_agency", new_callable=AsyncMock
    ):
        mock_load_agents.return_value = {}
        mock_construct_agency.return_value = MagicMock(spec=Agency)

        agency, returned_agency_id = await agency_manager.create_agency(agency_id=provided_id)

        assert agency is not None
        assert returned_agency_id == provided_id
        mock_load_agents.assert_called_once()
        mock_construct_agency.assert_called_once()


@pytest.mark.asyncio
async def test_create_agency(agency_manager):
    with patch(
        "nalgonda.dependencies.agency_manager.AgencyManager.load_and_construct_agents", new_callable=AsyncMock
    ) as mock_load_agents, patch(
        "nalgonda.dependencies.agency_manager.AgencyManager.construct_agency"
    ) as mock_construct_agency, patch(
        "nalgonda.dependencies.agency_manager.AgencyManager.cache_agency", new_callable=AsyncMock
    ):
        # Mock return value with necessary agents
        mock_load_agents.return_value = {"agent1": MagicMock(spec=Agent)}
        mock_construct_agency.return_value = MagicMock(spec=Agency)

        agency, agency_id = await agency_manager.create_agency()

        assert agency is not None
        assert isinstance(agency_id, str)
        mock_load_agents.assert_called_once()
        mock_construct_agency.assert_called_once()


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
        owner_id="test_owner_id",
        agents=["agent1"],
        agency_chart=["agent1"],
        agency_manifesto="manifesto",
    )
    updated_data = {"agency_manifesto": "new_manifesto"}

    with patch.object(agency_manager, "repopulate_cache", new_callable=AsyncMock) as mock_repopulate:
        await agency_manager.update_agency(agency_config, updated_data)

        assert agency_config.agency_manifesto == "new_manifesto"
        mock_repopulate.assert_called_once_with("test_agency")


@pytest.mark.asyncio
async def test_repopulate_cache_no_config(agency_manager):
    with patch("nalgonda.dependencies.agency_manager.AgencyConfigFirestoreStorage") as mock_storage_class, patch(
        "nalgonda.dependencies.agency_manager.logger"
    ) as mock_logger, patch("asyncio.to_thread", new_callable=AsyncMock) as mock_async_to_thread:
        mock_async_to_thread.return_value = None

        result = await agency_manager.repopulate_cache("nonexistent_agency_id")
        assert result is None
        mock_async_to_thread.assert_called_once()
        mock_logger.error.assert_called_once_with("Agency with id nonexistent_agency_id not found.")
        mock_storage_class.assert_called_once()


@pytest.mark.asyncio
async def test_repopulate_cache_success(agency_manager):
    agency_config = AgencyConfig(
        agency_id="test_agency",
        owner_id="test_owner_id",
        agents=["agent1"],
        agency_chart=["agent1"],
        agency_manifesto="manifesto",
    )
    agent = MagicMock(spec=Agent)

    with patch("nalgonda.dependencies.agency_manager.AgencyConfigFirestoreStorage") as mock_storage_class, patch(
        "nalgonda.dependencies.agency_manager.AgencyManager.load_and_construct_agents", new_callable=AsyncMock
    ) as mock_load_agents, patch(
        "nalgonda.dependencies.agency_manager.AgencyManager.construct_agency"
    ) as mock_construct_agency, patch(
        "nalgonda.dependencies.agency_manager.RedisCacheManager.set", new_callable=AsyncMock
    ) as mock_cache_set, patch("asyncio.to_thread", new_callable=AsyncMock) as mock_async_to_thread:
        mock_async_to_thread.return_value = agency_config
        mock_load_agents.return_value = {"agent1": agent}
        mock_construct_agency.return_value = Agency([], "manifesto")

        result = await agency_manager.repopulate_cache("test_agency")
        assert result is not None
        mock_async_to_thread.assert_called_once()
        mock_load_agents.assert_called_once_with(agency_config)
        mock_construct_agency.assert_called_once_with(agency_config, {"agent1": agent})
        mock_cache_set.assert_called_once_with("test_agency", result)

        mock_storage_class.assert_called_once()


# Test successful agent construction
@pytest.mark.asyncio
async def test_load_and_construct_agents_success():
    agency_config = AgencyConfig(
        agency_id="test_agency",
        owner_id="test_owner",
        agents=["agent1"],
        agency_chart=["agent1"],
        agency_manifesto="Test manifesto",
    )
    agent_config_mock = MagicMock(
        agent_id="agent1", role="test_role", description="Test Agent", instructions="Test Instructions", tools=["tool1"]
    )

    with patch("nalgonda.dependencies.agency_manager.AgentConfigFirestoreStorage") as mock_agent_storage_class:
        mock_agent_storage_class.return_value.load = MagicMock(return_value=agent_config_mock)
        agency_manager = AgencyManager(redis=MagicMock())
        agents = await agency_manager.load_and_construct_agents(agency_config)

        assert "test_role" in agents
        assert isinstance(agents["test_role"], Agent)
        assert agents["test_role"].id == "agent1"


# Test agent not found
@pytest.mark.asyncio
async def test_load_and_construct_agents_agent_not_found():
    agency_config = AgencyConfig(
        agency_id="test_agency",
        owner_id="test_owner",
        agents=["agent1"],
        agency_chart=["agent1"],
        agency_manifesto="Test manifesto",
    )

    with patch("nalgonda.dependencies.agency_manager.AgentConfigFirestoreStorage") as mock_agent_storage_class, patch(
        "logging.Logger.error"
    ) as mock_logger_error:
        mock_agent_storage_class.return_value.load = MagicMock(return_value=None)
        agency_manager = AgencyManager(redis=MagicMock())
        agents = await agency_manager.load_and_construct_agents(agency_config)

        assert agents == {}
        mock_logger_error.assert_called_with("Agent with id agent1 not found.")
