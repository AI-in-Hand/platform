from unittest.mock import MagicMock

import pytest

from nalgonda.repositories.env_config_firestore_storage import EnvConfigFirestoreStorage
from nalgonda.services.env_config_manager import EnvConfigManager
from nalgonda.services.env_vars_manager import ContextEnvVarsManager


# Utility function for setting up mocks
def setup_mocks(config_return_value):
    mocked_storage = MagicMock(spec=EnvConfigFirestoreStorage)
    mocked_storage.get_config.return_value = config_return_value
    ContextEnvVarsManager.get = MagicMock(return_value="owner123")
    return mocked_storage


# Test 1: Successful retrieval of an environment variable
def test_get_by_key_success():
    mocked_storage = setup_mocks({"TEST_KEY": "test_value"})
    manager = EnvConfigManager(env_config_storage=mocked_storage)
    assert manager.get_by_key("TEST_KEY") == "test_value"
    mocked_storage.get_config.assert_called_once_with("owner123")


# Test 2: Retrieval with non-existing key
def test_get_by_key_non_existing():
    mocked_storage = setup_mocks({"ANOTHER_KEY": "another_value"})
    manager = EnvConfigManager(env_config_storage=mocked_storage)
    with pytest.raises(ValueError) as exc_info:
        manager.get_by_key("MISSING_KEY")
    assert "MISSING_KEY not found for the given user." in str(exc_info.value)


# Test 3: No environment variables are set for the user
def test_get_by_key_no_env_vars_set():
    mocked_storage = setup_mocks(None)
    manager = EnvConfigManager(env_config_storage=mocked_storage)
    with pytest.raises(ValueError) as exc_info:
        manager.get_by_key("ANY_KEY")
    assert "Environment variables not set for the user: owner123" in str(exc_info.value)


# Test 4: Retrieval with empty configuration
def test_get_by_key_empty_configuration():
    mocked_storage = setup_mocks({})
    manager = EnvConfigManager(env_config_storage=mocked_storage)
    with pytest.raises(ValueError) as exc_info:
        manager.get_by_key("ANY_KEY")
    assert "Environment variables not set for the user: owner123" in str(exc_info.value)
