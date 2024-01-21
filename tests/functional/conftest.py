import pytest
from fastapi.testclient import TestClient

from nalgonda.dependencies.auth import get_current_active_user
from nalgonda.main import app, v1_api_app
from tests.test_utils import get_current_active_user_override, get_current_superuser_override


@pytest.fixture
def mock_get_current_active_user():
    v1_api_app.dependency_overrides[get_current_active_user] = get_current_active_user_override
    yield
    v1_api_app.dependency_overrides[get_current_active_user] = get_current_active_user


@pytest.fixture
def mock_get_current_superuser():
    v1_api_app.dependency_overrides[get_current_active_user] = get_current_superuser_override
    yield
    v1_api_app.dependency_overrides[get_current_active_user] = get_current_active_user


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
