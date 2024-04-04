import pytest

from backend.repositories.skill_config_firestore_storage import SkillConfigFirestoreStorage
from backend.services.adapters.agent_adapter import AgentAdapter


@pytest.fixture
def skill_config_storage() -> SkillConfigFirestoreStorage:
    return SkillConfigFirestoreStorage()


@pytest.fixture
def agent_adapter(skill_config_storage) -> AgentAdapter:
    return AgentAdapter(skill_config_storage)
