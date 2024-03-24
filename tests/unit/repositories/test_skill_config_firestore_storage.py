import pytest

from nalgonda.models.skill_config import SkillConfig
from nalgonda.repositories.skill_config_firestore_storage import SkillConfigFirestoreStorage
from tests.test_utils import TEST_USER_ID


@pytest.fixture
def skill_data():
    return {
        "id": "skill1",
        "owner_id": TEST_USER_ID,
        "title": "Example Skill",
        "version": 1,
        "content": 'print("Hello, World!")',
        "approved": False,
    }


def test_load_skill_config_by_user_id(mock_firestore_client, skill_data):
    mock_firestore_client.setup_mock_data("skill_configs", "skill1", skill_data)

    storage = SkillConfigFirestoreStorage()
    loaded_skill_configs = storage.load_by_owner_id(skill_data["owner_id"])

    expected_skill_config = SkillConfig.model_validate(skill_data)
    assert loaded_skill_configs == [expected_skill_config]


def test_load_skill_config_by_id(mock_firestore_client, skill_data):
    mock_firestore_client.setup_mock_data("skill_configs", "skill1", skill_data)

    storage = SkillConfigFirestoreStorage()
    loaded_skill_config = storage.load_by_id(skill_data["id"])

    expected_skill_config = SkillConfig.model_validate(skill_data)
    assert loaded_skill_config == expected_skill_config


def test_save_new_skill_config(mock_firestore_client, skill_data):
    # Test case for creating a new skill config
    mock_firestore_client.setup_mock_data("skill_configs", "skill2", skill_data, doc_id="skill2")

    new_skill_data = skill_data.copy()
    del new_skill_data["id"]  # Simulate a new skill without an id
    skill_config = SkillConfig(**new_skill_data)

    storage = SkillConfigFirestoreStorage()
    skill_id, _ = storage.save(skill_config)

    assert skill_id == "skill2"

    serialized_data = skill_config.model_dump()
    assert mock_firestore_client.to_dict() == serialized_data
    assert skill_config.id == "skill2"


def test_update_existing_skill_config(mock_firestore_client, skill_data):
    # Test case for updating an existing skill config
    mock_firestore_client.setup_mock_data("skill_configs", "skill1", skill_data)

    skill_config = SkillConfig(**skill_data)
    storage = SkillConfigFirestoreStorage()
    storage.save(skill_config)

    serialized_data = skill_config.model_dump()
    assert mock_firestore_client.to_dict() == serialized_data
    assert skill_config.id == skill_data["id"]
