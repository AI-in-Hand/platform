from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_env_config_firestore_storage():
    return MagicMock(name="EnvConfigFirestoreStorage")


@pytest.fixture
def mock_env_config_manager(recover_oai_client):  # noqa: ARG001
    with patch("nalgonda.services.oai_client.EnvConfigManager") as mock:
        yield mock


@pytest.fixture
def mock_openai_client(recover_oai_client):  # noqa: ARG001
    with patch("nalgonda.services.oai_client.openai.OpenAI") as mock:
        yield mock


@pytest.fixture
def mock_instructor_patch(recover_oai_client):  # noqa: ARG001
    with patch("nalgonda.services.oai_client.instructor.patch") as mock:
        mock.return_value = MagicMock(name="OpenAI_Client_Patched")
        yield mock


def test_get_openai_client_uses_correct_api_key(
    mock_env_config_manager, mock_openai_client, mock_env_config_firestore_storage, mock_instructor_patch
):
    # Setup
    from nalgonda.services.oai_client import get_openai_client

    expected_api_key = "test_api_key"
    mock_env_config_manager.return_value.get_by_key.return_value = expected_api_key

    # Execute
    client = get_openai_client(mock_env_config_firestore_storage)

    # Verify
    mock_env_config_manager.assert_called_with(mock_env_config_firestore_storage)
    mock_env_config_manager.return_value.get_by_key.assert_called_with("OPENAI_API_KEY")
    mock_openai_client.assert_called_with(api_key=expected_api_key, max_retries=5)
    mock_instructor_patch.assert_called_once()
    assert client == mock_instructor_patch.return_value, "The function should return a patched OpenAI client"
