from unittest.mock import patch

from nalgonda.models.agent_config import AgentConfig


def test_get_agent_config(client):
    with patch("nalgonda.routers.v1.api.agent.AgentConfigFirestoreStorage.load") as mock_load:
        agent_id = "agent1"
        mock_load.return_value = AgentConfig(
            agent_id=agent_id,
            role="ExampleRole",
            owner_id="user123",
            description="An example agent.",
            instructions="Do something important.",
            files_folder="agent_files/",
            tools=["tool1", "tool2"],
        )

        response = client.get(f"/v1/api/agent/config?agent_id={agent_id}")
        assert response.status_code == 200
        assert response.json() == {
            "agent_id": "agent1",
            "role": "ExampleRole",
            "owner_id": "user123",
            "description": "An example agent.",
            "instructions": "Do something important.",
            "files_folder": "agent_files/",
            "tools": ["tool1", "tool2"],
        }
