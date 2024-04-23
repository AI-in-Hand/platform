from unittest.mock import patch

import httpx
import pytest
from httpx import Request
from openai import AuthenticationError as OpenAIAuthenticationError
from pydantic import ValidationError

from backend.dependencies.dependencies import get_agency_adapter
from backend.models.agency_config import AgencyConfig
from backend.repositories.agency_config_storage import AgencyConfigStorage
from backend.repositories.agent_flow_spec_storage import AgentFlowSpecStorage


@pytest.fixture
def mock_agency_adapter_to_raise_pydantic_validation_error():
    from backend.main import api_app

    def raise_error():
        raise ValidationError.from_exception_data("Validation Error", line_errors=[])

    api_app.dependency_overrides[get_agency_adapter] = raise_error
    yield
    api_app.dependency_overrides[get_agency_adapter] = get_agency_adapter


@pytest.fixture
def mock_agent_storage_to_raise_openai_authentication_error():
    request = Request(method="GET", url="http://testserver/api/v1/agent?id=123")
    response = httpx.Response(401, request=request)
    exception = OpenAIAuthenticationError("Authentication Error", response=response, body={})
    with patch.object(AgentFlowSpecStorage, "load_by_id", side_effect=exception):
        yield


@pytest.fixture
def mock_agent_storage_to_raise_unhandled_exception():
    with patch.object(AgencyConfigStorage, "load_by_id", side_effect=Exception("Unhandled Exception")):
        yield


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
    assert "Validation error" in response.json()["data"]["message"]


@pytest.mark.usefixtures("mock_get_current_user")
def test_http_exception(client):
    response = client.get("/api/v1/agent?id=123")
    assert response.status_code == 404
    assert "message" in response.json()["data"]
    assert "Agent not found" in response.json()["data"]["message"]


@pytest.mark.usefixtures("mock_get_current_user", "mock_agent_storage_to_raise_openai_authentication_error")
def test_openai_authentication_error(client, caplog):
    caplog.set_level("WARNING")
    response = client.get("/api/v1/agent?id=123")
    assert response.status_code == 401
    assert "message" in response.json()["data"]
    assert "Authentication Error" in response.json()["data"]["message"]
    assert "request: http://testserver/api/v1/agent?id=123 exc: Authentication Error" in caplog.text


@pytest.mark.usefixtures("mock_get_current_user", "mock_agent_storage_to_raise_unhandled_exception")
def test_unhandled_exception(client, caplog):
    caplog.set_level("ERROR")

    with pytest.raises(Exception, match="Unhandled Exception") as exc_info:
        client.get("/api/v1/agency?id=123")

    assert exc_info.type is Exception
    assert "Unhandled Exception" in caplog.text
    assert "request: http://testserver/api/v1/agency?id=123" in caplog.text
