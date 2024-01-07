from unittest.mock import AsyncMock, patch

AGENT_ID = "agent1"
MOCK_DATA = {
    "agent_id": AGENT_ID,
    "owner_id": "user123",
    "role": "ExampleRole",
    "description": "An example agent.",
    "instructions": "Do something important.",
    "files_folder": "agent_files/",
    "tools": ["tool1", "tool2"],
}


def test_get_agent_config(client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, MOCK_DATA.copy())

    response = client.get(f"/v1/api/agent/config?agent_id={AGENT_ID}")
    assert response.status_code == 200
    assert response.json() == MOCK_DATA


def test_update_agent_config(client):
    agent_config_data = MOCK_DATA.copy()

    with patch(
        "nalgonda.dependencies.agent_manager.AgentManager.create_or_update_agent", new_callable=AsyncMock
    ) as mock_create_or_update_agent:
        mock_create_or_update_agent.return_value = AGENT_ID
        response = client.put("/v1/api/agent/config", json=agent_config_data)

    assert response.status_code == 200
    assert response.json() == {"agent_id": AGENT_ID}
