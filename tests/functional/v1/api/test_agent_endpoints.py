from unittest.mock import AsyncMock, patch

import pytest

from backend.models.skill_config import SkillConfig
from tests.testing_utils import TEST_USER_ID

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
        "timestamp": "2024-04-04T09:39:13.048457+00:00",
        "skills": [
            SkillConfig(title="GenerateProposal", approved=True).model_dump(),
            SkillConfig(title="SearchWeb", approved=True).model_dump(),
        ],
        "description": "An example agent.",
        "user_id": TEST_USER_ID,
    }


@pytest.fixture
def mock_agent_data_db(mock_agent_data_api):
    db_config = mock_agent_data_api.copy()
    db_config["skills"] = ["GenerateProposal", "SearchWeb"]
    return db_config


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agent_list(mock_agent_data_api, mock_agent_data_db, client, mock_firestore_client):
    # define a template agent configuration
    mock_agent_data_db_template = mock_agent_data_db.copy()
    mock_agent_data_db_template["id"] = "agent2"
    mock_agent_data_db_template["user_id"] = None

    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, mock_agent_data_db)
    mock_firestore_client.setup_mock_data("agent_configs", "agent2", mock_agent_data_db_template)
    mock_firestore_client.setup_mock_data(
        "skill_configs", "GenerateProposal", {"title": "GenerateProposal", "approved": True}
    )
    mock_firestore_client.setup_mock_data("skill_configs", "SearchWeb", {"title": "SearchWeb", "approved": True})

    response = client.get("/v1/api/agent/list")
    assert response.status_code == 200
    assert response.json()["data"] == [mock_agent_data_api]


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agent_list_owned_by_user(mock_agent_data_api, mock_agent_data_db, client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, mock_agent_data_db)
    mock_firestore_client.setup_mock_data(
        "skill_configs", "GenerateProposal", {"title": "GenerateProposal", "approved": True}
    )
    mock_firestore_client.setup_mock_data("skill_configs", "SearchWeb", {"title": "SearchWeb", "approved": True})

    response = client.get("/v1/api/agent/list?owned_by_user=true")
    assert response.status_code == 200
    assert response.json()["data"] == [mock_agent_data_api]


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_agent_config(client, mock_agent_data_api, mock_agent_data_db, mock_firestore_client):
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, mock_agent_data_db)
    mock_firestore_client.setup_mock_data(
        "skill_configs", "GenerateProposal", {"title": "GenerateProposal", "approved": True}
    )
    mock_firestore_client.setup_mock_data("skill_configs", "SearchWeb", {"title": "SearchWeb", "approved": True})

    response = client.get(f"/v1/api/agent?id={AGENT_ID}")
    assert response.status_code == 200
    assert response.json()["data"] == mock_agent_data_api


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_agent_success(client, mock_agent_data_api, mock_agent_data_db, mock_firestore_client):
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, mock_agent_data_db)
    mock_firestore_client.setup_mock_data(
        "skill_configs", "GenerateProposal", {"title": "GenerateProposal", "approved": True}
    )
    mock_firestore_client.setup_mock_data("skill_configs", "SearchWeb", {"title": "SearchWeb", "approved": True})

    with patch("backend.services.agent_manager.AgentManager") as mock_agent_manager:
        mock_agent_manager.return_value = AsyncMock()
        mock_agent_manager.return_value.create_or_update_agent.return_value = AGENT_ID

        response = client.put("/v1/api/agent", json=mock_agent_data_api)

    assert response.status_code == 200
    assert response.json()["data"] == {"id": AGENT_ID}


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_agent_user_id_mismatch(client, mock_agent_data_api, mock_agent_data_db, mock_firestore_client):
    agent_data_db = mock_agent_data_db.copy()
    agent_data_db["user_id"] = "other_user"
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, agent_data_db)

    response = client.put("/v1/api/agent", json=mock_agent_data_api)

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_agent_invalid_skill(client, mock_agent_data_api, mock_agent_data_db, mock_firestore_client):
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, mock_agent_data_db)
    mock_agent_data_api["skills"] = [
        SkillConfig(title="NonExistentSkill").model_dump(),
        SkillConfig(title="SearchWeb").model_dump(),
    ]

    with patch("backend.services.agent_manager.AgentManager") as mock_agent_manager:
        mock_agent_manager.return_value = AsyncMock()
        mock_agent_manager.return_value.create_or_update_agent.return_value = AGENT_ID

        response = client.put("/v1/api/agent", json=mock_agent_data_api)

    assert response.status_code == 400
    assert response.json() == {"detail": "Some skills are not supported: {'NonExistentSkill'}"}


@pytest.mark.usefixtures("mock_get_current_user")
def test_delete_agent_success(client, mock_agent_data_db, mock_firestore_client):
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, mock_agent_data_db)

    with patch("backend.services.agent_manager.AgentManager") as mock_agent_manager:
        mock_agent_manager.return_value = AsyncMock()
        mock_agent_manager.return_value.delete_agent.return_value = AGENT_ID

        response = client.delete(f"/v1/api/agent?id={AGENT_ID}")

    assert response.status_code == 200
    assert response.json() == {"status": True, "message": "Agent configuration deleted"}


@pytest.mark.usefixtures("mock_get_current_user")
def test_delete_agent_user_id_mismatch(client, mock_agent_data_db, mock_firestore_client):
    agent_data_db = mock_agent_data_db.copy()
    agent_data_db["user_id"] = "other_user"
    mock_firestore_client.setup_mock_data("agent_configs", AGENT_ID, agent_data_db)

    response = client.delete(f"/v1/api/agent?id={AGENT_ID}")

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}
