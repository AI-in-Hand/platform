import pytest

from nalgonda.models.agent_config import AgentConfig
from nalgonda.persistence.agent_config_firestore_storage import AgentConfigFirestoreStorage


@pytest.fixture
def agent_data():
    return {
        "agent_id": "agent1",
        "name": "example_name",
        "owner_id": "owner123",
        "description": "An example agent",
        "instructions": "Do something important",
        "files_folder": None,
        "tools": ["tool1", "tool2"],
    }


def test_load_agent_config(mock_firestore_client, agent_data):
    # Setup mock data
    # setup_mock_data(collection_name, document_name, data)
    mock_firestore_client.setup_mock_data("agent_configs", "agent1", agent_data)

    storage = AgentConfigFirestoreStorage()
    loaded_agent_config = storage.load_by_agent_id(agent_data["agent_id"])

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
    # Remove agent_id to simulate a new agent
    del new_agent_data["agent_id"]
    agent_config = AgentConfig(**new_agent_data)

    storage = AgentConfigFirestoreStorage()
    storage.save(agent_config)

    serialized_data = agent_config.model_dump()
    serialized_data["agent_id"] = None
    assert mock_firestore_client.to_dict() == serialized_data
    # Check that the agent_id was updated
    assert agent_config.agent_id == "new_agent_id"
