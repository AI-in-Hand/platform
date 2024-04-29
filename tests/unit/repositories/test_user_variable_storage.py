import pytest

from backend.repositories.user_variable_storage import UserVariableStorage
from tests.testing_utils import TEST_USER_ID


@pytest.fixture
@pytest.mark.usefixtures("mock_firestore_client")
def user_variable_storage():
    return UserVariableStorage()


def test_get_all_variables(user_variable_storage, mock_firestore_client):
    mock_firestore_client.setup_mock_data(
        "user_variables", TEST_USER_ID, {"VARIABLE1": "value1", "VARIABLE2": "value2"}
    )
    variables = user_variable_storage.get_all_variables(TEST_USER_ID)
    assert variables == {"VARIABLE1": "value1", "VARIABLE2": "value2"}


@pytest.mark.usefixtures("mock_firestore_client")
def test_get_all_variables_no_variables(user_variable_storage):
    variables = user_variable_storage.get_all_variables(TEST_USER_ID)
    assert variables is None


def test_set_variables(user_variable_storage, mock_firestore_client):
    variables = {"VARIABLE1": "value1", "VARIABLE2": "value2"}
    user_variable_storage.set_variables(TEST_USER_ID, variables)
    updated_variables = mock_firestore_client.collection("user_variables").document(TEST_USER_ID).to_dict()
    assert updated_variables == variables


def test_update_variables(user_variable_storage, mock_firestore_client):
    mock_firestore_client.setup_mock_data(
        "user_variables", TEST_USER_ID, {"VARIABLE1": "value1", "VARIABLE2": "value2"}
    )
    variables = {"VARIABLE2": "new_value2", "VARIABLE3": "value3"}
    user_variable_storage.update_variables(TEST_USER_ID, variables)
    updated_variables = mock_firestore_client.collection("user_variables").document(TEST_USER_ID).to_dict()
    assert updated_variables == {"VARIABLE1": "value1", "VARIABLE2": "new_value2", "VARIABLE3": "value3"}
