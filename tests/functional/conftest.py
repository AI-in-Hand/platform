import pytest
from fastapi.testclient import TestClient

from backend.dependencies.auth import get_current_user
from tests.testing_utils import get_current_superuser_override, get_current_user_override


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
