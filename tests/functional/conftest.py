import pytest
from fastapi.testclient import TestClient

from nalgonda.dependencies.auth import get_current_active_user
from tests.test_utils import get_current_active_user_override, get_current_superuser_override


@pytest.mark.usefixtures("mock_setup_logging")
@pytest.fixture
def mock_get_current_active_user():
    from nalgonda.main import v1_api_app

    v1_api_app.dependency_overrides[get_current_active_user] = get_current_active_user_override
    yield
    v1_api_app.dependency_overrides[get_current_active_user] = get_current_active_user


@pytest.mark.usefixtures("mock_setup_logging")
@pytest.fixture
def mock_get_current_superuser():
    from nalgonda.main import v1_api_app

    v1_api_app.dependency_overrides[get_current_active_user] = get_current_superuser_override
    yield
    v1_api_app.dependency_overrides[get_current_active_user] = get_current_active_user


@pytest.mark.usefixtures("mock_setup_logging")
@pytest.fixture
def client():
    from nalgonda.main import app

    with TestClient(app) as client:
        yield client
