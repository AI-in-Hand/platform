import pytest

from backend.repositories.env_config_firestore_storage import EnvConfigFirestoreStorage
from tests.test_utils import TEST_USER_ID


@pytest.fixture
def env_config_data():
    return {"API_KEY": "abc123", "SECRET_KEY": "s3cr3t"}


def test_get_config_exists(mock_firestore_client, env_config_data):
    # Setup mock data
    mock_firestore_client.setup_mock_data("env_configs", TEST_USER_ID, env_config_data)

    storage = EnvConfigFirestoreStorage()
    fetched_config = storage.get_config(TEST_USER_ID)

    assert fetched_config == env_config_data, "Fetched environment config should match the setup data"


@pytest.mark.usefixtures("mock_firestore_client")
def test_get_config_not_exists():
    # Assume no setup data, simulating a non-existent config
    storage = EnvConfigFirestoreStorage()
    fetched_config = storage.get_config(TEST_USER_ID)

    assert fetched_config is None, "Should return None if config does not exist"


def test_set_config_new(mock_firestore_client, env_config_data):
    # Assume no initial setup data, simulating setting a new config
    storage = EnvConfigFirestoreStorage()
    storage.set_config(TEST_USER_ID, env_config_data)

    # Assuming mock_firestore_client.to_dict() retrieves the last set data for the document
    assert mock_firestore_client.to_dict() == env_config_data, "The newly set config should match the input data"


def test_set_config_update(mock_firestore_client, env_config_data):
    # Setup initial data to simulate an update
    mock_firestore_client.setup_mock_data("env_configs", TEST_USER_ID, env_config_data)

    updated_config = env_config_data.copy()
    updated_config["NEW_VAR"] = "newValue"
    storage = EnvConfigFirestoreStorage()
    storage.set_config(TEST_USER_ID, updated_config)

    assert mock_firestore_client.to_dict() == updated_config, "The updated config should reflect the new changes"
