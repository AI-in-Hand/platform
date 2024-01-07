from unittest.mock import MagicMock, patch

import pytest

from nalgonda.models.tool_config import ToolConfig
from nalgonda.persistence.tool_config_firestore_storage import ToolConfigFirestoreStorage


@pytest.fixture
def tool_data():
    return {
        "tool_id": "tool1",
        "owner_id": "user123",
        "name": "Example Tool",
        "version": 1,
        "code": 'print("Hello, World!")',
        "approved": False,
    }


@pytest.fixture
def mock_firestore():
    with patch("nalgonda.persistence.tool_config_firestore_storage.firestore.client") as mock:
        yield mock


class TestToolConfigFirestoreStorage:
    def test_load_tool_config_by_user_id(self, mock_firestore, tool_data):
        mock_query = MagicMock()
        mock_query.stream.return_value = [MagicMock(to_dict=lambda: tool_data)]
        mock_collection = MagicMock(where=lambda _, __, ___: mock_query)
        mock_firestore.return_value.collection.return_value = mock_collection

        storage = ToolConfigFirestoreStorage()
        loaded_tool_configs = storage.load_by_user_id(tool_data["owner_id"])

        expected_tool_config = ToolConfig.model_validate(tool_data)
        assert loaded_tool_configs == [expected_tool_config]

    def test_load_tool_config_by_tool_id(self, mock_firestore, tool_data):
        mock_document_snapshot = MagicMock(exists=True, to_dict=lambda: tool_data)
        mock_document = MagicMock(get=lambda: mock_document_snapshot)
        mock_collection = MagicMock(document=lambda _: mock_document)
        mock_firestore.return_value.collection.return_value = mock_collection

        storage = ToolConfigFirestoreStorage()
        loaded_tool_config = storage.load_by_tool_id(tool_data["tool_id"])

        expected_tool_config = ToolConfig.model_validate(tool_data)
        assert loaded_tool_config == expected_tool_config

    def test_save_new_tool_config(self, mock_firestore, tool_data):
        # Test case for creating a new tool config
        mock_document = MagicMock()
        mock_add = MagicMock(return_value=MagicMock(id="tool2"))
        mock_collection = MagicMock(document=lambda _: mock_document)
        mock_collection.add = mock_add
        mock_firestore.return_value.collection.return_value = mock_collection

        new_tool_data = tool_data.copy()
        del new_tool_data["tool_id"]  # Simulate a new tool without a tool_id
        tool_config = ToolConfig(**new_tool_data)

        storage = ToolConfigFirestoreStorage()
        storage.save(tool_config)

        serialized_data = tool_config.model_dump()
        serialized_data["tool_id"] = None
        mock_add.assert_called_once_with(serialized_data)
        assert tool_config.tool_id == "tool2"

    def test_update_existing_tool_config(self, mock_firestore, tool_data):
        # Test case for updating an existing tool config
        mock_document = MagicMock()
        mock_collection = MagicMock(document=lambda _: mock_document)
        mock_firestore.return_value.collection.return_value = mock_collection

        tool_config = ToolConfig(**tool_data)
        storage = ToolConfigFirestoreStorage()
        storage.save(tool_config)

        serialized_data = tool_config.model_dump()
        mock_document.set.assert_called_once_with(serialized_data)
        assert tool_config.tool_id == tool_data["tool_id"]
