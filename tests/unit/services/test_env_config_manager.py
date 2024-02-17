from unittest.mock import patch

import pytest

from nalgonda.repositories.env_config_firestore_storage import EnvConfigFirestoreStorage
from nalgonda.services.env_config_manager import EnvConfigManager
from tests.test_utils import TEST_USER_ID


# Test 1: Successful retrieval of an environment variable
@patch("nalgonda.services.env_vars_manager.ContextEnvVarsManager.get", return_value=TEST_USER_ID)
def test_get_by_key_success(mock_get, mock_firestore_client):
    mock_firestore_client.setup_mock_data("env_configs", TEST_USER_ID, {"TEST_KEY": "test_value"})
    manager = EnvConfigManager(env_config_storage=EnvConfigFirestoreStorage())
    assert manager.get_by_key("TEST_KEY") == "test_value"
    mock_get.assert_called_once()


# Test 2: Retrieval with non-existing key
@patch("nalgonda.services.env_vars_manager.ContextEnvVarsManager.get", return_value=TEST_USER_ID)
def test_get_by_key_non_existing(mock_get, mock_firestore_client):
    mock_firestore_client.setup_mock_data("env_configs", TEST_USER_ID, {"ANOTHER_KEY": "another_value"})
    manager = EnvConfigManager(env_config_storage=EnvConfigFirestoreStorage())
    with pytest.raises(ValueError) as exc_info:
        manager.get_by_key("MISSING_KEY")
    assert "MISSING_KEY not found for the given user." in str(exc_info.value)
    mock_get.assert_called_once()


# Test 3: No environment variables are set for the user
@patch("nalgonda.services.env_vars_manager.ContextEnvVarsManager.get", return_value=TEST_USER_ID)
def test_get_by_key_no_env_vars_set(mock_get):
    manager = EnvConfigManager(env_config_storage=EnvConfigFirestoreStorage())
    with pytest.raises(ValueError) as exc_info:
        manager.get_by_key("ANY_KEY")
    assert f"Environment variables not set for the user: {TEST_USER_ID}" in str(exc_info.value)
    mock_get.assert_called_once()


# Test 4: Retrieval with empty configuration
@patch("nalgonda.services.env_vars_manager.ContextEnvVarsManager.get", return_value=TEST_USER_ID)
def test_get_by_key_empty_configuration(mock_get, mock_firestore_client):
    mock_firestore_client.setup_mock_data("env_configs", TEST_USER_ID, {})
    manager = EnvConfigManager(env_config_storage=EnvConfigFirestoreStorage())
    with pytest.raises(ValueError) as exc_info:
        manager.get_by_key("ANY_KEY")
    assert f"Environment variables not set for the user: {TEST_USER_ID}" in str(exc_info.value)
    mock_get.assert_called_once()
