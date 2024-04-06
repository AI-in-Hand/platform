import pytest

from backend.models.agency_config import AgencyConfig
from backend.repositories.agency_config_storage import AgencyConfigStorage
from tests.testing_utils.constants import TEST_AGENCY_ID, TEST_USER_ID


@pytest.fixture
def agency_config_data():
    return {"id": TEST_AGENCY_ID, "user_id": TEST_USER_ID, "name": "Test Agency"}


def test_load_agency_config_by_user_id(mock_firestore_client, agency_config_data):
    mocked_data = AgencyConfig.model_validate(agency_config_data)
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_config_data)

    storage = AgencyConfigStorage()
    result = storage.load_by_user_id(TEST_USER_ID)

    assert len(result) == 1
    assert result[0] == mocked_data


def test_load_agency_config_by_id(mock_firestore_client, agency_config_data):
    mocked_data = AgencyConfig.model_validate(agency_config_data)
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_config_data)

    storage = AgencyConfigStorage()
    result = storage.load_by_id(TEST_AGENCY_ID)

    assert result == mocked_data


def test_save_new_agency_config(mock_firestore_client):
    new_agency_data = {"user_id": TEST_USER_ID, "name": "New Test Agency"}
    new_agency_config = AgencyConfig.model_validate(new_agency_data)
    mock_firestore_client.setup_mock_data(
        "agency_configs", "new_test_agency_id", new_agency_data, doc_id="new_test_agency_id"
    )

    storage = AgencyConfigStorage()
    id_ = storage.save(new_agency_config)

    assert id_ is not None


def test_save_existing_agency_config(mock_firestore_client, agency_config_data):
    agency_config = AgencyConfig.model_validate(agency_config_data)
    mock_firestore_client.setup_mock_data("agency_configs", agency_config.id, agency_config_data)

    storage = AgencyConfigStorage()
    id_ = storage.save(agency_config)

    # Assert
    assert id_ == agency_config.id
    saved_data = mock_firestore_client.collection("agency_configs").document(id_).get().to_dict()
    assert saved_data == agency_config.model_dump()


def test_delete_agency_config(mock_firestore_client, agency_config_data):
    agency_config = AgencyConfig.model_validate(agency_config_data)
    mock_firestore_client.setup_mock_data(
        "agency_configs", agency_config.id, agency_config_data, doc_id=agency_config.id
    )

    storage = AgencyConfigStorage()
    storage.delete(agency_config.id)

    # Assert
    assert mock_firestore_client.to_dict() == {}
