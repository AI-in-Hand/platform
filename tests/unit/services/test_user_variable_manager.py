from unittest.mock import patch

import pytest

from backend.exceptions import UnsetVariableError
from backend.repositories.agent_flow_spec_storage import AgentFlowSpecStorage
from backend.repositories.user_variable_storage import UserVariableStorage
from backend.services.encryption_service import EncryptionService
from backend.services.user_variable_manager import UserVariableManager
from backend.settings import settings
from tests.testing_utils import TEST_USER_ID


# Test 1: Successful retrieval of a variable
@patch("backend.services.context_vars_manager.ContextEnvVarsManager.get", return_value=TEST_USER_ID)
def test_get_by_key_success(mock_get, mock_firestore_client):
    test_value = "gAAAAABl-O4Ls1gPlo6wBQw65vexUSBxL_pD2t8Sm-UjE8vdhDNmvKtrBLVIS5cpYWVvqQFb_6Uu6yKvU2las_5G50DtiKp_Kw=="
    mock_firestore_client.setup_mock_data("user_variables", TEST_USER_ID, {"TEST_KEY": test_value})
    manager = UserVariableManager(user_variable_storage=UserVariableStorage(), agent_storage=AgentFlowSpecStorage())
    assert manager.get_by_key("TEST_KEY") == "test_value"
    mock_get.assert_called_once()


# Test 2: Retrieval with non-existing key / empty configuration
@pytest.mark.parametrize("mock_user_variables", [{"ANOTHER_KEY": "another_value"}, {}])
@patch("backend.services.context_vars_manager.ContextEnvVarsManager.get", return_value=TEST_USER_ID)
def test_get_by_key_non_existing(mock_get, mock_firestore_client, mock_user_variables):
    mock_firestore_client.setup_mock_data("user_variables", TEST_USER_ID, mock_user_variables)
    manager = UserVariableManager(user_variable_storage=UserVariableStorage(), agent_storage=AgentFlowSpecStorage())
    with pytest.raises(UnsetVariableError) as exc_info:
        manager.get_by_key("MISSING_KEY")
    assert "Variable MISSING_KEY is not set" in str(exc_info)
    mock_get.assert_called_once()


# Test 3: No context variables are set for the user
@patch("backend.services.context_vars_manager.ContextEnvVarsManager.get", return_value=TEST_USER_ID)
def test_get_by_key_no_variables_set(mock_get):
    manager = UserVariableManager(user_variable_storage=UserVariableStorage(), agent_storage=AgentFlowSpecStorage())
    with pytest.raises(UnsetVariableError) as exc_info:
        manager.get_by_key("ANY_KEY")
    assert "Variable ANY_KEY is not set" in str(exc_info)
    mock_get.assert_called_once()


# Test 4: No context variables are set for the user
@pytest.mark.usefixtures("mock_firestore_client")
def test_get_by_key_no_user_id():
    manager = UserVariableManager(user_variable_storage=UserVariableStorage(), agent_storage=AgentFlowSpecStorage())
    with pytest.raises(ValueError) as exc_info:
        manager.get_by_key("ANY_KEY")
    assert "user_id not found in the context variables." in str(exc_info.value)


# Test 5: Successful setting of a variable
@patch("backend.services.context_vars_manager.ContextEnvVarsManager.get", return_value=TEST_USER_ID)
def test_set_by_key_success(mock_get, mock_firestore_client):
    new_value = "new_test_value"
    manager = UserVariableManager(user_variable_storage=UserVariableStorage(), agent_storage=AgentFlowSpecStorage())
    manager.set_by_key("NEW_KEY", new_value)

    updated_variables = mock_firestore_client.collection("user_variables").document(TEST_USER_ID).to_dict()
    assert "NEW_KEY" in updated_variables
    assert EncryptionService(settings.encryption_key).decrypt(updated_variables["NEW_KEY"]) == new_value
    mock_get.assert_called_once()


# Test 6: Attempt to set a variable when user_id is missing
@patch("backend.services.context_vars_manager.ContextEnvVarsManager.get", return_value=None)
def test_set_by_key_no_user_id(mock_get):
    manager = UserVariableManager(user_variable_storage=UserVariableStorage(), agent_storage=AgentFlowSpecStorage())
    with pytest.raises(ValueError) as exc_info:
        manager.set_by_key("SOME_KEY", "some_value")
    assert "user_id not found in the context variables." in str(exc_info.value)
    mock_get.assert_called_once()


# Test 7: Attempt to set a variable when no context variables are configured for the user
@patch("backend.services.context_vars_manager.ContextEnvVarsManager.get", return_value=TEST_USER_ID)
def test_set_by_key_no_variables_configured(mock_get, mock_firestore_client):
    mock_firestore_client.setup_mock_data("user_variables", TEST_USER_ID, None)  # Simulate no existing variables
    manager = UserVariableManager(user_variable_storage=UserVariableStorage(), agent_storage=AgentFlowSpecStorage())

    manager.set_by_key("NEW_KEY", "new_value")

    updated_variables = mock_firestore_client.collection("user_variables").document(TEST_USER_ID).to_dict()
    assert "NEW_KEY" in updated_variables
    # Check if the new key's value is correctly encrypted and stored
    assert EncryptionService(settings.encryption_key).decrypt(updated_variables["NEW_KEY"]) == "new_value"
    mock_get.assert_called_once()


# Test 8: Successful retrieval of variable names
def test_get_variable_names_success(mock_firestore_client):
    mock_firestore_client.setup_mock_data(
        "user_variables", TEST_USER_ID, {"VARIABLE1": "value1", "VARIABLE2": "value2"}
    )
    manager = UserVariableManager(user_variable_storage=UserVariableStorage(), agent_storage=AgentFlowSpecStorage())
    variable_names = manager.get_variable_names(TEST_USER_ID)
    assert variable_names == ["OPENAI_API_KEY", "VARIABLE1", "VARIABLE2"]


# Test 9: Retrieval of variable names when no variables exist
def test_get_variable_names_no_variables(mock_firestore_client):
    mock_firestore_client.setup_mock_data("user_variables", TEST_USER_ID, {})
    manager = UserVariableManager(user_variable_storage=UserVariableStorage(), agent_storage=AgentFlowSpecStorage())
    variable_names = manager.get_variable_names(TEST_USER_ID)
    assert variable_names == ["OPENAI_API_KEY"]


# Test 10: Successful creation of variables
def test_create_variables_success(mock_firestore_client):
    variables = {"VARIABLE1": "value1", "VARIABLE2": "value2"}
    manager = UserVariableManager(user_variable_storage=UserVariableStorage(), agent_storage=AgentFlowSpecStorage())
    manager.create_or_update_variables(TEST_USER_ID, variables)
    updated_variables = mock_firestore_client.to_dict()
    assert len(updated_variables) == 2
    for key, value in variables.items():
        assert key in updated_variables
        assert EncryptionService(settings.encryption_key).decrypt(updated_variables[key]) == value


# Test 11: Successful update of existing variables
def test_update_variables_success(mock_firestore_client):
    mock_firestore_client.setup_mock_data(
        "user_variables", TEST_USER_ID, {"VARIABLE1": "value1", "VARIABLE2": "value2", "VARIABLE4": "value4"}
    )
    variables = {"VARIABLE1": "new_value", "VARIABLE2": "", "VARIABLE3": "value3"}

    manager = UserVariableManager(user_variable_storage=UserVariableStorage(), agent_storage=AgentFlowSpecStorage())
    manager.create_or_update_variables(TEST_USER_ID, variables)

    updated_variables = mock_firestore_client.to_dict()
    assert len(updated_variables) == 3
    assert EncryptionService(settings.encryption_key).decrypt(updated_variables["VARIABLE1"]) == "new_value"
    assert updated_variables["VARIABLE2"] == "value2"
    assert EncryptionService(settings.encryption_key).decrypt(updated_variables["VARIABLE3"]) == "value3"
