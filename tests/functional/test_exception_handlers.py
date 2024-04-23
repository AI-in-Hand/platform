import httpx
import pytest
from openai import AuthenticationError as OpenAIAuthenticationError
from pydantic import ValidationError

from backend.dependencies.dependencies import get_agency_adapter
from backend.models.agency_config import AgencyConfig


@pytest.fixture
def mock_agency_adapter_to_raise_pydantic_validation_error():
    from backend.main import api_app

    def raise_error():
        raise ValidationError.from_exception_data("Validation Error", line_errors=[])

    api_app.dependency_overrides[get_agency_adapter] = raise_error
    yield
    api_app.dependency_overrides[get_agency_adapter] = get_agency_adapter


@pytest.fixture
def mock_agency_adapter_to_raise_openai_authentication_error():
    from backend.main import api_app

    def raise_error():
        raise OpenAIAuthenticationError("Authentication Error", response=httpx.Response(401), body={})

    api_app.dependency_overrides[get_agency_adapter] = raise_error
    yield
    api_app.dependency_overrides[get_agency_adapter] = get_agency_adapter


@pytest.fixture
def mock_agency_adapter_to_raise_unhandled_exception():
    from backend.main import api_app

    def raise_error():
        raise Exception("Unhandled Exception")

    api_app.dependency_overrides[get_agency_adapter] = raise_error
    yield
    api_app.dependency_overrides[get_agency_adapter] = get_agency_adapter


@pytest.mark.usefixtures("mock_get_current_user", "mock_agency_adapter_to_raise_pydantic_validation_error")
def test_pydantic_validation_error(caplog, client, agency_adapter, mock_firestore_client, mock_agent_data_db):
    caplog.set_level(10)

    agency_data_db = {
        "id": "existing_agency",
        "name": "Existing Agency",
        "shared_instructions": "Existing",
        "main_agent": "Sender Agent",
        "agents": ["sender_agent_id"],
        "flows": [],
    }
    mock_firestore_client.setup_mock_data("agency_configs", "existing_agency", agency_data_db)
    mock_firestore_client.setup_mock_data("agent_configs", "sender_agent_id", mock_agent_data_db)
    agency_data_api = agency_adapter.to_api(AgencyConfig(**agency_data_db)).model_dump()

    response = client.put("/api/v1/agency", json=agency_data_api)

    assert response.status_code == 400
    assert "message" in response.json()["data"]
    assert "Validation Error" in caplog.text


@pytest.mark.usefixtures("mock_get_current_user")
def test_request_validation_error(client):
    response = client.put("/api/v1/agent", json={})
    assert response.status_code == 422
    assert "message" in response.json()["data"]
    assert "validation error" in response.json()["data"]["message"].lower()


@pytest.mark.usefixtures("mock_get_current_user")
def test_http_exception(client):
    response = client.get("/api/v1/agent?id=123")
    assert response.status_code == 404
    assert "message" in response.json()["data"]
    assert "not found" in response.json()["data"]["message"].lower()


# @pytest.mark.usefixtures("mock_get_current_user")
# def test_openai_authentication_error(client, mock_agency_adapter_to_raise_openai_authentication_error):
#     response = client.get("/api/v1/agent?id=123")
#     assert response.status_code == 401
#     assert "message" in response.json()["data"]
#     assert "unauthorized" in response.json()["data"]["message"].lower()


@pytest.mark.usefixtures("mock_get_current_user", "mock_agency_adapter_to_raise_unhandled_exception")
def test_unhandled_exception(client):
    response = client.get("/api/v1/agent?id=123")
    assert response.status_code == 500
    assert "message" in response.json()["data"]
    assert "internal server error" in response.json()["data"]["message"].lower()
