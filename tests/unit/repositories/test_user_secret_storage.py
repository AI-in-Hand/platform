import pytest

from backend.repositories.user_secret_storage import UserSecretStorage
from tests.testing_utils import TEST_USER_ID


@pytest.fixture
@pytest.mark.usefixtures("mock_firestore_client")
def user_secret_storage():
    return UserSecretStorage()


def test_get_all_secrets(user_secret_storage, mock_firestore_client):
    mock_firestore_client.setup_mock_data("user_secrets", TEST_USER_ID, {"SECRET1": "value1", "SECRET2": "value2"})
    secrets = user_secret_storage.get_all_secrets(TEST_USER_ID)
    assert secrets == {"SECRET1": "value1", "SECRET2": "value2"}


@pytest.mark.usefixtures("mock_firestore_client")
def test_get_all_secrets_no_secrets(user_secret_storage):
    secrets = user_secret_storage.get_all_secrets(TEST_USER_ID)
    assert secrets is None


def test_set_secrets(user_secret_storage, mock_firestore_client):
    secrets = {"SECRET1": "value1", "SECRET2": "value2"}
    user_secret_storage.set_secrets(TEST_USER_ID, secrets)
    updated_secrets = mock_firestore_client.collection("user_secrets").document(TEST_USER_ID).to_dict()
    assert updated_secrets == secrets


def test_update_secrets(user_secret_storage, mock_firestore_client):
    mock_firestore_client.setup_mock_data("user_secrets", TEST_USER_ID, {"SECRET1": "value1", "SECRET2": "value2"})
    secrets = {"SECRET2": "new_value2", "SECRET3": "value3"}
    user_secret_storage.update_secrets(TEST_USER_ID, secrets)
    updated_secrets = mock_firestore_client.collection("user_secrets").document(TEST_USER_ID).to_dict()
    assert updated_secrets == {"SECRET1": "value1", "SECRET2": "new_value2", "SECRET3": "value3"}
