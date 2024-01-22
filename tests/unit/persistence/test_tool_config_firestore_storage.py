import pytest

from nalgonda.models.tool_config import ToolConfig
from nalgonda.persistence.tool_config_firestore_storage import ToolConfigFirestoreStorage
from tests.test_utils import TEST_USER_ID


@pytest.fixture
def tool_data():
    return {
        "tool_id": "tool1",
        "owner_id": TEST_USER_ID,
        "name": "Example Tool",
        "version": 1,
        "code": 'print("Hello, World!")',
        "approved": False,
    }


def test_load_tool_config_by_user_id(mock_firestore_client, tool_data):
    mock_firestore_client.setup_mock_data("tool_configs", "tool1", tool_data)

    storage = ToolConfigFirestoreStorage()
    loaded_tool_configs = storage.load_by_user_id(tool_data["owner_id"])

    expected_tool_config = ToolConfig.model_validate(tool_data)
    assert loaded_tool_configs == [expected_tool_config]


def test_load_tool_config_by_tool_id(mock_firestore_client, tool_data):
    mock_firestore_client.setup_mock_data("tool_configs", "tool1", tool_data)

    storage = ToolConfigFirestoreStorage()
    loaded_tool_config = storage.load_by_tool_id(tool_data["tool_id"])

    expected_tool_config = ToolConfig.model_validate(tool_data)
    assert loaded_tool_config == expected_tool_config


def test_save_new_tool_config(mock_firestore_client, tool_data):
    # Test case for creating a new tool config
    mock_firestore_client.setup_mock_data("tool_configs", "tool2", tool_data, doc_id="tool2")

    new_tool_data = tool_data.copy()
    del new_tool_data["tool_id"]  # Simulate a new tool without a tool_id
    tool_config = ToolConfig(**new_tool_data)

    storage = ToolConfigFirestoreStorage()
    tool_id, _ = storage.save(tool_config)

    assert tool_id == "tool2"

    serialized_data = tool_config.model_dump()
    assert mock_firestore_client.to_dict() == serialized_data
    assert tool_config.tool_id == "tool2"


def test_update_existing_tool_config(mock_firestore_client, tool_data):
    # Test case for updating an existing tool config
    mock_firestore_client.setup_mock_data("tool_configs", "tool1", tool_data)

    tool_config = ToolConfig(**tool_data)
    storage = ToolConfigFirestoreStorage()
    storage.save(tool_config)

    serialized_data = tool_config.model_dump()
    assert mock_firestore_client.to_dict() == serialized_data
    assert tool_config.tool_id == tool_data["tool_id"]
