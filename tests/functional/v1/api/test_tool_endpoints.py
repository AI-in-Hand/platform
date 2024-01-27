import pytest

from nalgonda.persistence.tool_config_firestore_storage import ToolConfigFirestoreStorage
from tests.test_utils import TEST_USER_ID


@pytest.fixture
def tool_config_data():
    return {
        "tool_id": "tool1",
        "owner_id": TEST_USER_ID,
        "name": "Tool 1",
        "version": 1,
        "code": 'print("Hello World")',
        "approved": False,
    }


def test_get_tool_list(tool_config_data, client, mock_firestore_client, mock_get_current_active_user):  # noqa: ARG001
    mock_firestore_client.setup_mock_data("tool_configs", "tool1", tool_config_data)

    response = client.get("/v1/api/tool/list")
    assert response.status_code == 200
    assert response.json() == [tool_config_data]


def test_approve_tool_config(tool_config_data, client, mock_firestore_client, mock_get_current_superuser):  # noqa: ARG001
    mock_firestore_client.setup_mock_data("tool_configs", "tool1", tool_config_data)

    response = client.post("/v1/api/tool/approve?tool_id=tool1")
    assert response.status_code == 200
    assert response.json() == {"message": "Tool configuration approved"}

    # Verify if the tool configuration is approved in the mock Firestore client
    updated_config = mock_firestore_client.to_dict()
    assert updated_config["approved"] is True


def test_update_tool_config_success(tool_config_data, client, mock_firestore_client, mock_get_current_active_user):  # noqa: ARG001
    mock_firestore_client.setup_mock_data("tool_configs", "tool1", tool_config_data)

    tool_config_data = tool_config_data.copy()
    tool_config_data["name"] = "Tool 1 Updated"
    tool_config_data["code"] = 'print("Hello World Updated")'
    response = client.post("/v1/api/tool", json=tool_config_data)
    assert response.status_code == 200
    assert response.json() == {"tool_id": "tool1", "tool_version": 2}

    # Verify if the tool configuration is updated in the mock Firestore client
    updated_config = ToolConfigFirestoreStorage().load_by_tool_id("tool1")
    assert updated_config.name == "Tool 1 Updated"
    assert updated_config.code == 'print("Hello World Updated")'
    assert updated_config.version == 2


def test_update_tool_config_owner_id_mismatch(
    tool_config_data,
    client,
    mock_firestore_client,
    mock_get_current_active_user,  # noqa: ARG001
):
    tool_config_data["owner_id"] = "another_user"

    mock_firestore_client.setup_mock_data("tool_configs", "tool1", tool_config_data)

    response = client.post("/v1/api/tool", json=tool_config_data)
    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}
