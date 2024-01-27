from unittest import mock
from unittest.mock import AsyncMock, patch

from nalgonda.models.agency_config import AgencyConfig
from tests.test_utils import TEST_USER_ID


def test_get_agency_config(client, mock_firestore_client, mock_get_current_active_user):  # noqa: ARG001
    mock_data = {
        "agency_id": "test_agency_id",
        "owner_id": TEST_USER_ID,
        "agency_manifesto": "Test Manifesto",
        "main_agent": None,
        "agents": [],
        "agency_chart": [],
    }
    mock_firestore_client.setup_mock_data("agency_configs", "test_agency_id", mock_data)

    response = client.get("/v1/api/agency?agency_id=test_agency_id")
    assert response.status_code == 200
    assert response.json() == mock_data


def test_get_agency_config_not_found(client, mock_get_current_active_user):  # noqa: ARG001
    # Simulate non-existent agency by not setting up any data for it
    response = client.get("/v1/api/agency?agency_id=non_existent_agency")
    assert response.status_code == 404
    assert response.json() == {"detail": "Agency configuration not found"}


def test_create_agency_success(client, mock_firestore_client, mock_get_current_active_user):  # noqa: ARG001
    template_config = {
        "agency_id": "template_agency_id",
        "agency_manifesto": "Manifesto",
        "agents": [],
        "agency_chart": [],
    }

    with patch(
        "nalgonda.services.agency_manager.AgencyManager.update_or_create_agency", new_callable=AsyncMock
    ) as mock_update_or_create_agency:
        response = client.put("/v1/api/agency?agency_id=test_agency_id", json=template_config)

    assert response.status_code == 200
    assert response.json() == {"agency_id": mock.ANY}

    template_config.update({"owner_id": TEST_USER_ID})
    model_template_config = AgencyConfig.model_validate(template_config)
    model_template_config.agency_id = mock.ANY
    assert mock_update_or_create_agency.mock_calls[0].args[0] == model_template_config
    assert mock_update_or_create_agency.mock_calls[0].args[0].agency_id != "template_agency_id"


def test_update_agency_success(client, mock_firestore_client, mock_get_current_active_user):  # noqa: ARG001
    # Setup initial data in mock Firestore client
    initial_data = {
        "agency_id": "test_agency_id",
        "owner_id": TEST_USER_ID,
        "agency_manifesto": "Original Manifesto",
        "agents": [],
        "main_agent": None,
        "agency_chart": [],
    }
    mock_firestore_client.setup_mock_data("agency_configs", "test_agency_id", initial_data)
    new_data = initial_data.copy()
    new_data.update({"agency_manifesto": "Updated Manifesto"})

    with patch(
        "nalgonda.services.agency_manager.AgencyManager.repopulate_cache_and_update_assistants", new_callable=AsyncMock
    ) as mock_repopulate_cache:
        response = client.put("/v1/api/agency?agency_id=test_agency_id", json=new_data)

    assert response.status_code == 200
    assert response.json() == {"agency_id": initial_data["agency_id"]}

    mock_repopulate_cache.assert_called_once_with("test_agency_id")

    assert mock_firestore_client.to_dict() == new_data


def test_update_agency_owner_id_mismatch(client, mock_firestore_client, mock_get_current_active_user):  # noqa: ARG001
    # Setup initial data in mock Firestore client
    initial_data = {
        "agency_id": "test_agency_id",
        "owner_id": "some_other_user",
        "agency_manifesto": "Original Manifesto",
        "agents": [],
        "main_agent": None,
        "agency_chart": [],
    }
    mock_firestore_client.setup_mock_data("agency_configs", "test_agency_id", initial_data)
    new_data = initial_data.copy()
    new_data.update({"agency_manifesto": "Updated Manifesto"})

    response = client.put("/v1/api/agency?agency_id=test_agency_id", json=new_data)

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}
