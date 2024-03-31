import pytest

from backend.models.agent_config import AgentConfig
from backend.repositories.agent_config_firestore_storage import AgentConfigFirestoreStorage
from tests.test_utils import TEST_USER_ID


@pytest.fixture
def agent_data():
    return {
        "id": "agent1",
        "name": "example_name",
        "user_id": TEST_USER_ID,
        "description": "An example agent",
        "instructions": "Do something important",
        "files_folder": None,
        "skills": ["skill1", "skill2"],
    }


def test_load_agent_config(mock_firestore_client, agent_data):
    # Setup mock data
    # setup_mock_data(collection_name, document_name, data)
    mock_firestore_client.setup_mock_data("agent_configs", "agent1", agent_data)

    storage = AgentConfigFirestoreStorage()
    loaded_agent_config = storage.load_by_id(agent_data["id"])

    expected_agent_config = AgentConfig.model_validate(agent_data)
    assert loaded_agent_config == expected_agent_config


def test_save_existing_agent_config(mock_firestore_client, agent_data):
    mock_firestore_client.setup_mock_data("agent_configs", "agent1", agent_data)

    agent_config = AgentConfig(**agent_data)
    storage = AgentConfigFirestoreStorage()
    storage.save(agent_config)

    serialized_data = agent_config.model_dump()
    assert mock_firestore_client.to_dict() == serialized_data


def test_save_new_agent_config(mock_firestore_client, agent_data):
    mock_firestore_client.setup_mock_data("agent_configs", "new_agent_id", agent_data, doc_id="new_agent_id")

    new_agent_data = agent_data.copy()
    # Remove agent id to simulate a new agent
    del new_agent_data["id"]
    agent_config = AgentConfig(**new_agent_data)

    storage = AgentConfigFirestoreStorage()
    storage.save(agent_config)

    serialized_data = agent_config.model_dump()
    assert mock_firestore_client.to_dict() == serialized_data
    # Check that the agent id was updated
    assert agent_config.id == "new_agent_id"
