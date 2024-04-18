import pytest
from fastapi.testclient import TestClient

from backend.dependencies.auth import get_current_user
from tests.testing_utils import TEST_USER_ID, get_current_superuser_override, get_current_user_override
from tests.testing_utils.constants import TEST_AGENCY_ID


@pytest.mark.usefixtures("mock_setup_logging")
@pytest.fixture
def mock_get_current_user():
    from backend.main import api_app

    api_app.dependency_overrides[get_current_user] = get_current_user_override
    yield
    api_app.dependency_overrides[get_current_user] = get_current_user


@pytest.mark.usefixtures("mock_setup_logging")
@pytest.fixture
def mock_get_current_superuser():
    from backend.main import api_app

    api_app.dependency_overrides[get_current_user] = get_current_superuser_override
    yield
    api_app.dependency_overrides[get_current_user] = get_current_user


@pytest.mark.usefixtures("mock_setup_logging")
@pytest.fixture
def client():
    from backend.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_session_storage(mock_firestore_client):
    session_data = {
        "id": "test_session_id",
        "user_id": TEST_USER_ID,
        "agency_id": TEST_AGENCY_ID,
        "timestamp": "2021-01-01T00:00:00Z",
    }
    mock_firestore_client.setup_mock_data("session_configs", "test_session_id", session_data)
