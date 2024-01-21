from tests.test_utils import TEST_USER_ID


def test_get_tool_list(client, mock_firestore_client, mock_get_current_active_user):
    user_id = TEST_USER_ID
    tool_config_data = {
        "tool_id": "tool1",
        "owner_id": user_id,
        "name": "Tool 1",
        "version": 1,
        "code": 'print("Hello World")',
        "approved": False,
    }
    mock_firestore_client.setup_mock_data("tool_configs", "tool1", tool_config_data)

    response = client.get("/v1/api/tool")
    assert response.status_code == 200
    assert response.json() == [tool_config_data]

    mock_get_current_active_user.assert_called_once()


def test_approve_tool_config(client, mock_firestore_client, mock_get_current_superuser):
    tool_id = "tool1"
    tool_config_data = {
        "tool_id": tool_id,
        "owner_id": "user1",
        "name": "Tool 1",
        "version": 1,
        "code": 'print("Hello")',
        "approved": False,
    }
    mock_firestore_client.setup_mock_data("tool_configs", tool_id, tool_config_data)

    response = client.put(f"/v1/api/tool/approve?tool_id={tool_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Tool configuration approved"}

    # Verify if the tool configuration is approved in the mock Firestore client
    updated_config = mock_firestore_client.to_dict()
    assert updated_config["approved"] is True

    mock_get_current_superuser.assert_called_once()
