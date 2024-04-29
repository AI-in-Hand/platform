from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_openai_client(recover_oai_client):  # noqa: ARG001
    with patch("backend.services.oai_client.openai.OpenAI") as mock:
        yield mock


@pytest.fixture
def mock_instructor_patch(recover_oai_client):  # noqa: ARG001
    with patch("backend.services.oai_client.instructor.patch") as mock:
        mock.return_value = MagicMock(name="OpenAI_Client_Patched")
        yield mock


def test_get_openai_client_uses_correct_api_key(mock_openai_client, mock_instructor_patch):
    # Setup
    from backend.services.oai_client import get_openai_client

    expected_api_key = "test_api_key"
    mock_user_variable_manager = MagicMock()
    mock_user_variable_manager.get_by_key.return_value = expected_api_key

    # Execute
    client = get_openai_client(mock_user_variable_manager)

    # Verify
    mock_user_variable_manager.get_by_key.assert_called_with("OPENAI_API_KEY")
    mock_openai_client.assert_called_with(api_key=expected_api_key, max_retries=5)
    mock_instructor_patch.assert_called_once()
    assert client == mock_instructor_patch.return_value, "The function should return a patched OpenAI client"


@pytest.mark.usefixtures("recover_oai_client")
def test_get_openai_client_raises_error_when_no_api_key_and_user_variable_manager():
    # Setup
    from backend.services.oai_client import get_openai_client

    # Execute
    with pytest.raises(ValueError) as e:
        get_openai_client()

    # Verify
    assert str(e.value) == "Either user_variable_manager or api_key must be provided"
