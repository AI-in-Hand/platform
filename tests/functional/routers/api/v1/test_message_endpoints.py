from unittest.mock import MagicMock, patch

import pytest
from agency_swarm import Agency

from backend.dependencies.dependencies import get_user_variable_manager
from backend.models.agency_config import AgencyConfig
from backend.repositories.agency_config_storage import AgencyConfigStorage
from backend.repositories.user_variable_storage import UserVariableStorage
from backend.services.agency_manager import AgencyManager
from tests.testing_utils import TEST_USER_ID
from tests.testing_utils.constants import TEST_AGENCY_ID


@pytest.fixture
@pytest.mark.usefixtures("mock_firestore_client")
def agency_manager():
    yield AgencyManager(
        agent_manager=MagicMock(),
        agency_config_storage=AgencyConfigStorage(),
        user_variable_manager=get_user_variable_manager(user_variable_storage=UserVariableStorage()),
    )


@pytest.fixture
def mock_construct_agency():
    with patch(
        "backend.services.agency_manager.AgencyManager._construct_agency_and_update_assistants"
    ) as mock_construct:
        mock_construct.return_value = MagicMock(spec=Agency)
        mock_construct.return_value.get_completion.return_value = "Hello, world!"
        yield mock_construct


@pytest.fixture
def message_data():
    return {"agency_id": TEST_AGENCY_ID, "session_id": "test_session_id", "content": "Hello, world!"}


# Successful retrieval of messages
@pytest.mark.usefixtures("mock_get_current_user", "mock_session_storage", "mock_openai_client")
def test_get_message_list_success(client):
    response = client.get("/api/v1/message/list?session_id=test_session_id")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["content"] == "Hello"
    assert response.json()[1]["content"] == "Hi"


# Session not found
@pytest.mark.usefixtures("mock_get_current_user", "mock_openai_client")
def test_get_message_list_session_not_found(client):
    response = client.get("/api/v1/message/list?session_id=nonexistent_session_id")
    assert response.status_code == 404
    assert response.json()["data"]["message"] == "Session not found"


# Current user not authorized
@pytest.mark.usefixtures("mock_get_current_user", "mock_session_storage", "mock_openai_client")
def test_get_message_list_unauthorized(client, mock_firestore_client):
    test_session_config = {
        "id": "test_session_id",
        "name": "Test agency",
        "user_id": "other_user_id",
        "agency_id": TEST_AGENCY_ID,
        "timestamp": "2021-01-01T00:00:00Z",
    }
    mock_firestore_client.setup_mock_data("session_configs", "test_session_id", test_session_config)

    response = client.get("/api/v1/message/list?session_id=test_session_id")
    assert response.status_code == 403
    assert response.json()["data"]["message"] == "You don't have permissions to access this session"


# Successful message sending
@pytest.mark.usefixtures("mock_get_current_user", "mock_session_storage")
def test_post_message_success(client, mock_construct_agency, mock_firestore_client, message_data):
    agency_data = {
        "user_id": TEST_USER_ID,
        "id": TEST_AGENCY_ID,
        "name": "Test Agency",
        "main_agent": "sender_agent_id",
    }
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_data)

    # Sending a message
    response = client.post("/api/v1/message", json=message_data)

    assert response.status_code == 200
    # We will check for the actual message we set up to be sent
    assert response.json()["data"] == {"content": "Hello, world!"}
    mock_construct_agency.assert_awaited_once_with(AgencyConfig(**agency_data), {})


# Agency/session configuration not found
@pytest.mark.usefixtures("mock_get_current_user", "mock_firestore_client", "mock_session_storage")
def test_post_message_404_error(client, message_data, mock_firestore_client):
    response = client.post("/api/v1/message", json=message_data)
    assert response.status_code == 404
    assert response.json()["data"]["message"] == "Agency not found"

    # second part: remove the session and check if the session not found error is raised
    mock_firestore_client.collection("session_configs").document("test_session_id").delete()
    response = client.post("/api/v1/message", json=message_data)
    assert response.status_code == 404
    assert response.json()["data"]["message"] == "Session not found"


# Current user not the owner of the agency
@pytest.mark.usefixtures("mock_get_current_user")
def test_post_message_unauthorized(
    client, mock_construct_agency, mock_firestore_client, message_data, session_config_data
):
    agency_data = {
        "user_id": "other_user_id",
        "id": TEST_AGENCY_ID,
        "name": "Test Agency",
        "main_agent": "sender_agent_id",
    }
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_data)
    mock_firestore_client.setup_mock_data("session_configs", "test_session_id", session_config_data)

    # Sending a message
    response = client.post("/api/v1/message", json=message_data)

    assert response.status_code == 403
    assert response.json()["data"]["message"] == "You don't have permissions to access this agency"
    mock_construct_agency.assert_not_called()


# Failure in message processing
@pytest.mark.usefixtures("mock_get_current_user")
def test_post_message_processing_failure(client, mock_construct_agency, mock_firestore_client, message_data):
    agency_data = {
        "user_id": TEST_USER_ID,
        "id": TEST_AGENCY_ID,
        "name": "Test Agency",
        "main_agent": "sender_agent_id",
    }
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_data)
    mock_firestore_client.setup_mock_data(
        "session_configs",
        "test_session_id",
        {
            "id": "test_session_id",
            "name": "Test agency",
            "user_id": TEST_USER_ID,
            "agency_id": TEST_AGENCY_ID,
            "thread_ids": {},
            "timestamp": "2021-01-01T00:00:00Z",
        },
    )

    mock_construct_agency.return_value.get_completion.side_effect = Exception("Something went wrong")

    # Sending a message
    response = client.post("/api/v1/message", json=message_data)

    assert response.status_code == 500
    assert response.json()["data"]["message"] == "Something went wrong"

    mock_construct_agency.assert_called_once_with(AgencyConfig(**agency_data), {})


@pytest.fixture
def mock_openai_client():
    with patch("backend.routers.api.v1.message.get_openai_client") as mock:
        mock.return_value.beta.threads.messages.list.return_value = [
            MagicMock(id="1", role="user", content=[MagicMock(text=MagicMock(value="Hello"))]),
            MagicMock(id="2", role="assistant", content=[MagicMock(text=MagicMock(value="Hi"))]),
        ]
        yield mock
