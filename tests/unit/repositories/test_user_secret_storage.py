import pytest

from backend.repositories.user_secret_storage import UserSecretStorage
from tests.test_utils import TEST_USER_ID


@pytest.fixture
def user_secret_data():
    return {"API_KEY": "abc123", "SECRET_KEY": "s3cr3t"}


def test_get_all_secrets_exists(mock_firestore_client, user_secret_data):
    # Setup mock data
    mock_firestore_client.setup_mock_data("user_secrets", TEST_USER_ID, user_secret_data)

    storage = UserSecretStorage()
    fetched_secrets = storage.get_all_secrets(TEST_USER_ID)

    assert fetched_secrets == user_secret_data, "Fetched secrets should match the setup data"


@pytest.mark.usefixtures("mock_firestore_client")
def test_get_all_secrets_not_exists():
    # Assume no setup data, simulating a non-existent document
    storage = UserSecretStorage()
    fetched_secrets = storage.get_all_secrets(TEST_USER_ID)

    assert fetched_secrets is None, "Should return None if document does not exist"


def test_set_secrets_new(mock_firestore_client, user_secret_data):
    # Assume no initial setup data, simulating setting a new document
    storage = UserSecretStorage()
    storage.set_secrets(TEST_USER_ID, user_secret_data)

    # Assuming mock_firestore_client.to_dict() retrieves the last set data for the document
    assert mock_firestore_client.to_dict() == user_secret_data, "The newly set document should match the input data"


def test_set_secrets_update(mock_firestore_client, user_secret_data):
    # Setup initial data to simulate an update
    mock_firestore_client.setup_mock_data("user_secrets", TEST_USER_ID, user_secret_data)

    updated_secrets = user_secret_data.copy()
    updated_secrets["NEW_VAR"] = "newValue"
    storage = UserSecretStorage()
    storage.set_secrets(TEST_USER_ID, updated_secrets)

    assert mock_firestore_client.to_dict() == updated_secrets, "The updated document should reflect the new changes"
