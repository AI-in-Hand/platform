from unittest.mock import MagicMock, patch

import pytest

from backend.repositories.skill_config_storage import SkillConfigStorage
from tests.testing_utils import TEST_USER_ID


@pytest.fixture
def skill_config_data():
    return {
        "id": "skill1",
        "user_id": TEST_USER_ID,
        "title": "Skill 1",
        "description": "",
        "version": 1,
        "timestamp": "2024-04-04T09:39:13.048457+00:00",
        "content": 'print("Hello World")',
        "approved": False,
    }


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_skill_list(skill_config_data, client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("skill_configs", "skill1", skill_config_data)

    response = client.get("/api/v1/skill/list")
    assert response.status_code == 200
    assert response.json()["data"] == [skill_config_data]


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_skill_config_success(skill_config_data, client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("skill_configs", skill_config_data["id"], skill_config_data)

    response = client.get(f"/api/v1/skill?id={skill_config_data['id']}")
    assert response.status_code == 200
    assert response.json()["data"] == skill_config_data


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_skill_config_forbidden(skill_config_data, client, mock_firestore_client):
    skill_config_data["user_id"] = "different_user"
    mock_firestore_client.setup_mock_data("skill_configs", skill_config_data["id"], skill_config_data)

    response = client.get(f"/api/v1/skill?id={skill_config_data['id']}")
    assert response.status_code == 403
    assert response.json() == {"data": {"message": "You don't have permissions to access this skill"}}


@pytest.mark.usefixtures("mock_get_current_user")
def test_get_skill_config_not_found(client):
    skill_id = "nonexistent_skill"
    response = client.get(f"/api/v1/skill?id={skill_id}")
    assert response.status_code == 404
    assert response.json() == {"data": {"message": "Skill not found"}}


@pytest.mark.usefixtures("mock_get_current_user")
def test_delete_skill_success(skill_config_data, client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("skill_configs", "skill1", skill_config_data)

    response = client.delete("/api/v1/skill?id=skill1")
    assert response.status_code == 200
    assert response.json() == {"status": True, "message": "Skill configuration deleted", "data": []}

    # Verify if the skill configuration is deleted in the mock Firestore client
    assert mock_firestore_client.to_dict() == {}


@pytest.mark.usefixtures("mock_get_current_user")
def test_delete_skill_forbidden(skill_config_data, client, mock_firestore_client):
    skill_config_data["user_id"] = "different_user"
    mock_firestore_client.setup_mock_data("skill_configs", "skill1", skill_config_data)

    response = client.delete("/api/v1/skill?id=skill1")
    assert response.status_code == 403
    assert response.json() == {"data": {"message": "You don't have permissions to access this skill"}}


@pytest.mark.usefixtures("mock_get_current_user")
def test_delete_skill_not_found(client):
    skill_id = "nonexistent_skill"
    response = client.delete(f"/api/v1/skill?id={skill_id}")
    assert response.status_code == 404
    assert response.json() == {"data": {"message": "Skill not found"}}


@pytest.mark.usefixtures("mock_get_current_superuser")
def test_approve_skill(skill_config_data, client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("skill_configs", "skill1", skill_config_data)

    response = client.post("/api/v1/skill/approve?id=skill1")
    assert response.status_code == 200
    assert response.json() == {"status": True, "message": "Skill configuration approved"}

    # Verify if the skill configuration is approved in the mock Firestore client
    updated_config = mock_firestore_client.to_dict()
    assert updated_config["approved"] is True


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_skill_config_success(skill_config_data, client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("skill_configs", "skill1", skill_config_data)

    skill_config_data = skill_config_data.copy()
    skill_config_data["title"] = "Skill 1 Updated"
    skill_config_data["content"] = 'print("Hello World Updated")'
    response = client.post("/api/v1/skill", json=skill_config_data)
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["id"] == "skill1"
    assert response.json()["message"] == "Version 2 of the skill skill1 created"

    # Verify if the skill configuration is updated in the mock Firestore client
    updated_config = SkillConfigStorage().load_by_id("skill1")
    assert updated_config.title == "Skill 1 Updated"
    assert updated_config.content == 'print("Hello World Updated")'
    assert updated_config.version == 2


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_skill_config_user_id_mismatch(skill_config_data, client, mock_firestore_client):
    skill_config_data["user_id"] = "another_user"

    mock_firestore_client.setup_mock_data("skill_configs", "skill1", skill_config_data)

    response = client.post("/api/v1/skill", json=skill_config_data)
    assert response.status_code == 403
    assert response.json() == {"data": {"message": "You don't have permissions to access this skill"}}


@pytest.mark.usefixtures("mock_get_current_user")
def test_update_skill_config_not_found(skill_config_data, client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("skill_configs", "skill1", skill_config_data)

    skill_config_data = skill_config_data.copy()
    skill_config_data["id"] = "nonexistent_skill"
    response = client.post("/api/v1/skill", json=skill_config_data)
    assert response.status_code == 404
    assert response.json() == {"data": {"message": "Skill not found"}}


@pytest.mark.usefixtures("mock_get_current_user")
@patch("backend.services.skill_executor.SkillExecutor.execute_skill", MagicMock(return_value="Execution result"))
def test_execute_skill_success(skill_config_data, client, mock_firestore_client):
    skill_config_data["approved"] = True
    mock_firestore_client.setup_mock_data("skill_configs", skill_config_data["id"], skill_config_data)

    response = client.post("/api/v1/skill/execute", json={"id": skill_config_data["id"], "user_prompt": "test prompt"})
    assert response.status_code == 200
    assert response.json()["data"] == "Execution result"


@pytest.mark.usefixtures("mock_get_current_user")
def test_execute_skill_not_found(client):
    skill_id = "nonexistent_skill"
    response = client.post("/api/v1/skill/execute", json={"id": skill_id, "user_prompt": "test prompt"})
    assert response.status_code == 404
    assert response.json() == {"data": {"message": "Skill not found"}}


@pytest.mark.usefixtures("mock_get_current_user")
def test_execute_skill_not_approved(skill_config_data, client, mock_firestore_client):
    mock_firestore_client.setup_mock_data("skill_configs", "skill1", skill_config_data)

    response = client.post("/api/v1/skill/execute", json={"id": "skill1", "user_prompt": "test prompt"})
    assert response.status_code == 403
    assert response.json() == {"data": {"message": "Skill not approved"}}
