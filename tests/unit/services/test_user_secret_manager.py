from unittest.mock import patch

import pytest

from backend.repositories.user_secret_storage import UserSecretStorage
from backend.services.encryption_service import EncryptionService
from backend.services.user_secret_manager import UserSecretManager
from backend.settings import settings
from tests.testing_utils import TEST_USER_ID


# Test 1: Successful retrieval of a secret
@patch("backend.services.context_vars_manager.ContextEnvVarsManager.get", return_value=TEST_USER_ID)
def test_get_by_key_success(mock_get, mock_firestore_client):
    test_value = "gAAAAABl-O4Ls1gPlo6wBQw65vexUSBxL_pD2t8Sm-UjE8vdhDNmvKtrBLVIS5cpYWVvqQFb_6Uu6yKvU2las_5G50DtiKp_Kw=="
    mock_firestore_client.setup_mock_data("user_secrets", TEST_USER_ID, {"TEST_KEY": test_value})
    manager = UserSecretManager(user_secret_storage=UserSecretStorage())
    assert manager.get_by_key("TEST_KEY") == "test_value"
    mock_get.assert_called_once()


# Test 2: Retrieval with non-existing key / empty configuration
@pytest.mark.parametrize("mock_user_secrets", [{"ANOTHER_KEY": "another_value"}, {}])
@patch("backend.services.context_vars_manager.ContextEnvVarsManager.get", return_value=TEST_USER_ID)
def test_get_by_key_non_existing(mock_get, mock_firestore_client, mock_user_secrets):
    mock_firestore_client.setup_mock_data("user_secrets", TEST_USER_ID, mock_user_secrets)
    manager = UserSecretManager(user_secret_storage=UserSecretStorage())
    with pytest.raises(ValueError) as exc_info:
        manager.get_by_key("MISSING_KEY")
    assert "Secret MISSING_KEY not set for the given user" in str(exc_info.value)
    mock_get.assert_called_once()


# Test 3: No context variables are set for the user
@patch("backend.services.context_vars_manager.ContextEnvVarsManager.get", return_value=TEST_USER_ID)
def test_get_by_key_no_secrets_set(mock_get):
    manager = UserSecretManager(user_secret_storage=UserSecretStorage())
    with pytest.raises(ValueError) as exc_info:
        manager.get_by_key("ANY_KEY")
    assert "Secret ANY_KEY not set for the given user" in str(exc_info.value)
    mock_get.assert_called_once()


# Test 4: Successful setting of a secret
@patch("backend.services.context_vars_manager.ContextEnvVarsManager.get", return_value=TEST_USER_ID)
def test_set_by_key_success(mock_get, mock_firestore_client):
    new_value = "new_test_value"
    manager = UserSecretManager(user_secret_storage=UserSecretStorage())
    manager.set_by_key("NEW_KEY", new_value)

    updated_secrets = mock_firestore_client.collection("user_secrets").document(TEST_USER_ID).to_dict()
    assert "NEW_KEY" in updated_secrets
    assert EncryptionService(settings.encryption_key).decrypt(updated_secrets["NEW_KEY"]) == new_value
    mock_get.assert_called_once()


# Test 5: Attempt to set a variable when user_id is missing
@patch("backend.services.context_vars_manager.ContextEnvVarsManager.get", return_value=None)
def test_set_by_key_no_user_id(mock_get):
    manager = UserSecretManager(user_secret_storage=UserSecretStorage())
    with pytest.raises(ValueError) as exc_info:
        manager.set_by_key("SOME_KEY", "some_value")
    assert "user_id not found in the context variables." in str(exc_info.value)
    mock_get.assert_called_once()


# Test 6: Attempt to set a variable when no context variables are configured for the user
@patch("backend.services.context_vars_manager.ContextEnvVarsManager.get", return_value=TEST_USER_ID)
def test_set_by_key_no_secrets_configured(mock_get, mock_firestore_client):
    mock_firestore_client.setup_mock_data("user_secrets", TEST_USER_ID, None)  # Simulate no existing secrets
    manager = UserSecretManager(user_secret_storage=UserSecretStorage())

    manager.set_by_key("NEW_KEY", "new_value")

    updated_secrets = mock_firestore_client.collection("user_secrets").document(TEST_USER_ID).to_dict()
    assert "NEW_KEY" in updated_secrets
    # Check if the new key's value is correctly encrypted and stored
    assert EncryptionService(settings.encryption_key).decrypt(updated_secrets["NEW_KEY"]) == "new_value"
    mock_get.assert_called_once()


# Test 7: Successful retrieval of secret names
def test_get_secret_names_success(mock_firestore_client):
    mock_firestore_client.setup_mock_data("user_secrets", TEST_USER_ID, {"SECRET1": "value1", "SECRET2": "value2"})
    manager = UserSecretManager(user_secret_storage=UserSecretStorage())
    secret_names = manager.get_secret_names(TEST_USER_ID)
    assert secret_names == ["SECRET1", "SECRET2"]


# Test 8: Retrieval of secret names when no secrets exist
def test_get_secret_names_no_secrets(mock_firestore_client):
    mock_firestore_client.setup_mock_data("user_secrets", TEST_USER_ID, {})
    manager = UserSecretManager(user_secret_storage=UserSecretStorage())
    secret_names = manager.get_secret_names(TEST_USER_ID)
    assert secret_names == []


# Test 9: Successful update of secrets
def test_update_secrets_success(mock_firestore_client):
    secrets = {"SECRET1": "value1", "SECRET2": "value2"}
    manager = UserSecretManager(user_secret_storage=UserSecretStorage())
    manager.update_secrets(TEST_USER_ID, secrets)
    updated_secrets = mock_firestore_client.collection("user_secrets").document(TEST_USER_ID).to_dict()
    assert len(updated_secrets) == 2
    for key, value in secrets.items():
        assert key in updated_secrets
        assert EncryptionService(settings.encryption_key).decrypt(updated_secrets[key]) == value
