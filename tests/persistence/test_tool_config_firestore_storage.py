from unittest.mock import AsyncMock, MagicMock, patch

from nalgonda.models.tool_config import ToolConfig
from nalgonda.persistence.tool_config_firestore_storage import ToolConfigFirestoreStorage


class TestToolConfigFirestoreStorage:
    @patch("nalgonda.persistence.tool_config_firestore_storage.firestore.Client", MagicMock())
    def test_load_tool_config_by_user_id(self):
        user_id = "user123"
        tool_data = {
            "tool_id": "tool1",
            "owner_id": user_id,
            "name": "Example Tool",
            "version": 1,
            "code": 'print("Hello, World!")',
            "approved": False,
        }
        tool_config = ToolConfig(**tool_data)

        storage = ToolConfigFirestoreStorage()
        storage.collection.where.return_value.stream.return_value = [
            AsyncMock(to_dict=MagicMock(return_value=tool_data))
        ]

        loaded_tool_configs = storage.load_by_user_id(user_id)

        assert loaded_tool_configs == [tool_config]

    def test_save_tool_config(self):
        tool_id = "tool1"
        tool_config = ToolConfig(
            tool_id=tool_id,
            owner_id="user123",
            name="Example Tool",
            version=1,
            code='print("Hello, World!")',
            approved=False,
        )

        storage = ToolConfigFirestoreStorage()
        storage.save(tool_config)

        storage.collection.document(tool_id).set.assert_called_once()
