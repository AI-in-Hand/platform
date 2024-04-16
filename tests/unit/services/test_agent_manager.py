from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from backend.models.agent_flow_spec import AgentFlowSpec
from backend.models.skill_config import SkillConfig
from backend.services.agent_manager import AgentManager
from tests.testing_utils import TEST_USER_ID
from tests.testing_utils.constants import TEST_AGENT_ID


@pytest.fixture
def agent_manager(storage_mock, user_secret_manager_mock, skill_storage_mock):
    return AgentManager(storage_mock, user_secret_manager_mock, skill_storage_mock)


@pytest.fixture
def storage_mock():
    return MagicMock()


@pytest.fixture
def user_secret_manager_mock():
    return MagicMock()


@pytest.fixture
def skill_storage_mock():
    return MagicMock()


@pytest.mark.asyncio
async def test_get_agent_list(agent_manager, storage_mock):
    user_configs = [AgentFlowSpec(user_id=TEST_USER_ID, config={"name": "Agent1"})]
    template_configs = [AgentFlowSpec(user_id=None, config={"name": "Agent2"})]
    storage_mock.load_by_user_id.side_effect = [user_configs, template_configs]

    result = await agent_manager.get_agent_list(TEST_USER_ID)

    assert result == user_configs + template_configs
    storage_mock.load_by_user_id.assert_any_call(TEST_USER_ID)
    storage_mock.load_by_user_id.assert_any_call(None)


@pytest.mark.asyncio
async def test_handle_agent_creation_or_update_new_agent(agent_manager, skill_storage_mock):
    config = AgentFlowSpec(config={"name": "Agent1"}, skills=["GenerateProposal"])
    skill_storage_mock.load_by_titles.return_value = [SkillConfig(title="GenerateProposal", approved=True)]
    agent_manager._create_or_update_agent = AsyncMock(return_value="new_agent_id")

    result = await agent_manager.handle_agent_creation_or_update(config, TEST_USER_ID)

    assert result == "new_agent_id"
    assert config.user_id == TEST_USER_ID
    skill_storage_mock.load_by_titles.assert_called_once_with(config.skills)
    agent_manager._create_or_update_agent.assert_awaited_once_with(config)


@pytest.mark.asyncio
async def test_handle_agent_creation_or_update_existing_agent(agent_manager, storage_mock, skill_storage_mock):
    config = AgentFlowSpec(
        id=TEST_AGENT_ID, config={"name": "Agent1"}, skills=["GenerateProposal"], user_id=TEST_USER_ID
    )
    config_db = AgentFlowSpec(id=TEST_AGENT_ID, user_id=TEST_USER_ID, config={"name": "Agent1"})
    storage_mock.load_by_id.return_value = config_db
    skill_storage_mock.load_by_titles.return_value = [SkillConfig(title="GenerateProposal", approved=True)]
    agent_manager._create_or_update_agent = AsyncMock(return_value="new_agent_id")

    result = await agent_manager.handle_agent_creation_or_update(config, TEST_USER_ID)

    assert result == "new_agent_id"
    storage_mock.load_by_id.assert_called_once_with(config.id)
    skill_storage_mock.load_by_titles.assert_called_once_with(config.skills)
    agent_manager._create_or_update_agent.assert_awaited_once_with(config)


@pytest.mark.asyncio
async def test_delete_agent(agent_manager, storage_mock):
    config = AgentFlowSpec(id=TEST_AGENT_ID, user_id=TEST_USER_ID, config={"name": "Agent1"})
    storage_mock.load_by_id.return_value = config

    await agent_manager.delete_agent(TEST_AGENT_ID, TEST_USER_ID)

    storage_mock.load_by_id.assert_called_once_with(TEST_AGENT_ID)
    storage_mock.delete.assert_called_once_with(TEST_AGENT_ID)


@pytest.mark.asyncio
async def test_delete_agent_not_found(agent_manager, storage_mock):
    storage_mock.load_by_id.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await agent_manager.delete_agent(TEST_AGENT_ID, TEST_USER_ID)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Agent not found"


@pytest.mark.asyncio
async def test_delete_agent_forbidden(agent_manager, storage_mock):
    config = AgentFlowSpec(id=TEST_AGENT_ID, user_id="user2", config={"name": "Agent1"})
    storage_mock.load_by_id.return_value = config

    with pytest.raises(HTTPException) as exc_info:
        await agent_manager.delete_agent(TEST_AGENT_ID, TEST_USER_ID)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "You don't have permissions to access this agent"
