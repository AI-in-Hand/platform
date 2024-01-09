import pytest
from fastapi.testclient import TestClient

from nalgonda.dependencies.auth import get_current_active_user
from nalgonda.main import app, v1_api_app
from tests.test_utils import get_current_active_user_override

v1_api_app.dependency_overrides[get_current_active_user] = get_current_active_user_override


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
