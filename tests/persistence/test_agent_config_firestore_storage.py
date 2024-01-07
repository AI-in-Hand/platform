from unittest.mock import AsyncMock, MagicMock, patch

from nalgonda.models.agent_config import AgentConfig
from nalgonda.persistence.agent_config_firestore_storage import AgentConfigFirestoreStorage


class TestAgentConfigFirestoreStorage:
    @patch("nalgonda.persistence.agent_config_firestore_storage.firestore.Client", MagicMock())
    def test_load_agent_config(self):
        agent_id = "agent1"
        agent_data = {
            "agent_id": agent_id,
            "role": "example_role",
            "owner_id": "owner123",
            "description": "An example agent",
            "instructions": "Do something important",
            "files_folder": "example_folder",
            "tools": ["tool1", "tool2"],
        }
        agent_config = AgentConfig(**agent_data)

        storage = AgentConfigFirestoreStorage()
        storage.collection.document(agent_id).get.return_value = AsyncMock(to_dict=MagicMock(return_value=agent_data))

        loaded_agent_config = storage.load(agent_id)

        assert loaded_agent_config == agent_config

    def test_save_agent_config(self):
        agent_id = "agent1"
        agent_config = AgentConfig(
            agent_id=agent_id,
            role="example_role",
            owner_id="owner123",
            description="An example agent",
            instructions="Do something important",
            files_folder="example_folder",
            tools=["tool1", "tool2"],
        )

        storage = AgentConfigFirestoreStorage()
        storage.save(agent_config)

        storage.collection.document(agent_id).set.assert_called_once()
