from unittest.mock import AsyncMock, patch

import pytest

from backend.models.skill_config import SkillConfig
from tests.test_utils import TEST_USER_ID

AGENT_ID = "agent1"


@pytest.fixture
def mock_agent_data_api():
    return {
        "id": AGENT_ID,
        "type": "userproxy",
        "config": {
            "name": "ExampleRole",
            "system_message": "Do something important.",
            "code_execution_config": {
                "work_dir": None,
                "use_docker": False,
            },
        },
        "timestamp": "2021-01-01T00:00:00Z",
        "skills": [SkillConfig(title="skill1").model_dump(), SkillConfig(title="skill2").model_dump()],
        "description": "An example agent.",
        "user_id": TEST_USER_ID,
    }


@pytest.fixture
def mock_agent_data_db(mock_agent_data_api):
    db_config = mock_agent_data_api.copy()
    db_config["skills"] = ["skill1", "skill2"]
    return db_config


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agent_list(mock_agent_data_api, mock_agent_data_db, client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, mock_agent_data_db)
    mock_firestore_client.setup_mock_data("skill_configs", "skill1", {"title": "skill1"})
    mock_firestore_client.setup_mock_data("skill_configs", "skill2", {"title": "skill2"})

    response = client.get("/v1/api/agent/list")
    assert response.status_code == 200
    assert response.json()["data"] == [mock_agent_data_api]


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agent_config(client, mock_agent_data_api, mock_agent_data_db, mock_firestore_client):
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, mock_agent_data_db)
    mock_firestore_client.setup_mock_data("skill_configs", "skill1", {"title": "skill1"})
    mock_firestore_client.setup_mock_data("skill_configs", "skill2", {"title": "skill2"})

    response = client.get(f"/v1/api/agent?id={AGENT_ID}")
    assert response.status_code == 200
    assert response.json()["data"] == mock_agent_data_api


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_agent_flow_spec_success(client, mock_agent_data_api, mock_agent_data_db, mock_firestore_client):
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, mock_agent_data_db)

    with patch("backend.services.agent_manager.AgentManager") as mock_agent_manager:
        mock_agent_manager.return_value = AsyncMock()
        mock_agent_manager.return_value.create_or_update_agent.return_value = AGENT_ID

        response = client.put("/v1/api/agent", json=mock_agent_data_api)

    assert response.status_code == 200
    assert response.json()["data"] == {"id": AGENT_ID}


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_agent_flow_spec_user_id_mismatch(
    client, mock_agent_data_api, mock_agent_data_db, mock_firestore_client
):
    agent_data_db = mock_agent_data_db.copy()
    agent_data_db["user_id"] = "other_user"
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, agent_data_db)

    response = client.put("/v1/api/agent", json=mock_agent_data_api)

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}
