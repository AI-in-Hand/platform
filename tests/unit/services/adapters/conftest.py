import pytest

from backend.repositories.skill_config_storage import SkillConfigStorage
from backend.services.adapters.agent_adapter import AgentAdapter


@pytest.fixture
def skill_config_storage() -> SkillConfigStorage:
    return SkillConfigStorage()


@pytest.fixture
def agent_adapter(skill_config_storage) -> AgentAdapter:
    return AgentAdapter(skill_config_storage)
