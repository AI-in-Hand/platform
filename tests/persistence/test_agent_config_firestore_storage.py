from unittest.mock import MagicMock, patch

import pytest

from nalgonda.models.agent_config import AgentConfig
from nalgonda.persistence.agent_config_firestore_storage import AgentConfigFirestoreStorage


@pytest.fixture
def agent_data():
    return {
        "agent_id": "agent1",
        "role": "example_role",
        "owner_id": "owner123",
        "description": "An example agent",
        "instructions": "Do something important",
        "files_folder": "example_folder",
        "tools": ["tool1", "tool2"],
    }


@pytest.fixture
def mock_firestore():
    with patch("nalgonda.persistence.agent_config_firestore_storage.firestore.client") as mock:
        yield mock


class TestAgentConfigFirestoreStorage:
    def test_load_agent_config(self, mock_firestore, agent_data):
        mock_document_snapshot = MagicMock(exists=True, to_dict=lambda: agent_data)
        mock_document = MagicMock(get=lambda: mock_document_snapshot)
        mock_collection = MagicMock(document=lambda _: mock_document)
        mock_firestore.return_value.collection.return_value = mock_collection

        storage = AgentConfigFirestoreStorage()
        loaded_agent_config = storage.load(agent_data["agent_id"])

        expected_agent_config = AgentConfig.model_validate(agent_data)
        assert loaded_agent_config == expected_agent_config

    def test_save_existing_agent_config(self, mock_firestore, agent_data):
        mock_document = MagicMock()
        mock_collection = MagicMock(document=lambda _: mock_document)
        mock_firestore.return_value.collection.return_value = mock_collection

        agent_config = AgentConfig(**agent_data)
        storage = AgentConfigFirestoreStorage()
        storage.save(agent_config)

        serialized_data = agent_config.model_dump()
        mock_document.set.assert_called_once_with(serialized_data)

    def test_save_new_agent_config(self, mock_firestore, agent_data):
        mock_add = MagicMock(return_value=[MagicMock(id="new_agent_id")])
        mock_collection = MagicMock(add=mock_add)
        mock_firestore.return_value.collection.return_value = mock_collection

        new_agent_data = agent_data.copy()
        # Remove agent_id to simulate a new agent
        del new_agent_data["agent_id"]
        agent_config = AgentConfig(**new_agent_data)

        storage = AgentConfigFirestoreStorage()
        storage.save(agent_config)

        serialized_data = agent_config.model_dump()
        serialized_data["agent_id"] = None
        mock_add.assert_called_once_with(serialized_data)
        # Check that the agent_id was updated
        assert agent_config.agent_id == "new_agent_id"
