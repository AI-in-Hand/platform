from unittest.mock import AsyncMock, patch

import pytest

from tests.test_utils import TEST_USER_ID

AGENT_ID = "agent1"


@pytest.fixture
def agent_config_data():
    return {
        "agent_id": AGENT_ID,
        "owner_id": TEST_USER_ID,
        "name": "ExampleRole",
        "description": "An example agent.",
        "instructions": "Do something important.",
        "files_folder": None,
        "skills": ["skill1", "skill2"],
    }


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agent_list(agent_config_data, client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, agent_config_data)

    response = client.get("/v1/api/agent/list")
    assert response.status_code == 200
    assert response.json() == [agent_config_data]


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agent_config(client, agent_config_data, mock_firestore_client):
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, agent_config_data)

    response = client.get(f"/v1/api/agent?agent_id={AGENT_ID}")
    assert response.status_code == 200
    assert response.json() == agent_config_data


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_agent_config_success(client, agent_config_data, mock_firestore_client):
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, agent_config_data)

    with patch("backend.services.agent_manager.AgentManager") as mock_agent_manager:
        mock_agent_manager.return_value = AsyncMock()
        mock_agent_manager.return_value.create_or_update_agent.return_value = AGENT_ID

        response = client.put("/v1/api/agent", json=agent_config_data)

    assert response.status_code == 200
    assert response.json() == {"agent_id": AGENT_ID}


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_agent_config_owner_id_mismatch(client, agent_config_data, mock_firestore_client):
    agent_data_db = agent_config_data.copy()
    agent_data_db["owner_id"] = "other_user"
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, agent_data_db)

    response = client.put("/v1/api/agent", json=agent_config_data)

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}
