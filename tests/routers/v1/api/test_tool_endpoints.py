from unittest.mock import patch

from nalgonda.models.tool_config import ToolConfig


def test_get_tool_configs(client):
    with patch("nalgonda.routers.v1.api.tool.ToolConfigFirestoreStorage.load_by_user_id") as mock_load_by_user_id:
        user_id = "user1"
        mock_load_by_user_id.return_value = [
            ToolConfig(
                tool_id="tool1", owner_id=user_id, name="Tool 1", version=1, code='print("Hello World")', approved=False
            )
        ]
        response = client.get(f"/v1/api/tool/config?user_id={user_id}")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["owner_id"] == user_id


def test_approve_tool_config(client):
    with patch(
        "nalgonda.routers.v1.api.tool.ToolConfigFirestoreStorage.load_by_tool_id"
    ) as mock_load_by_tool_id, patch("nalgonda.routers.v1.api.tool.ToolConfigFirestoreStorage.save") as mock_save:
        tool_id = "tool1"
        tool_config_instance = ToolConfig(
            tool_id=tool_id, owner_id="user1", name="Tool 1", version=1, code='print("Hello")', approved=False
        )
        mock_load_by_tool_id.return_value = tool_config_instance
        response = client.put(f"/v1/api/tool/approve?tool_id={tool_id}")
        assert response.status_code == 200
        tool_config_instance.approved = True
        mock_save.assert_called_once_with(tool_config_instance)
        assert response.json() == {"message": "Tool configuration approved"}
