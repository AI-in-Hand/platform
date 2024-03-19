import pytest

from nalgonda.models.agency_config import AgencyConfig
from nalgonda.repositories.agency_config_firestore_storage import AgencyConfigFirestoreStorage
from tests.test_utils.constants import TEST_AGENCY_ID, TEST_USER_ID


@pytest.fixture
def agency_config_data():
    return {"agency_id": TEST_AGENCY_ID, "owner_id": TEST_USER_ID, "name": "Test Agency"}


def test_load_agency_config_by_owner_id(mock_firestore_client, agency_config_data):
    mocked_data = AgencyConfig.model_validate(agency_config_data)
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_config_data)

    storage = AgencyConfigFirestoreStorage()
    result = storage.load_by_owner_id(TEST_USER_ID)

    assert len(result) == 1
    assert result[0] == mocked_data


def test_load_agency_config_by_agency_id(mock_firestore_client, agency_config_data):
    mocked_data = AgencyConfig.model_validate(agency_config_data)
    mock_firestore_client.setup_mock_data("agency_configs", TEST_AGENCY_ID, agency_config_data)

    storage = AgencyConfigFirestoreStorage()
    result = storage.load_by_agency_id(TEST_AGENCY_ID)

    assert result == mocked_data


def test_save_new_agency_config(mock_firestore_client):
    new_agency_data = {"owner_id": TEST_USER_ID, "name": "New Test Agency"}
    new_agency_config = AgencyConfig.model_validate(new_agency_data)
    mock_firestore_client.setup_mock_data(
        "agency_configs", "new_test_agency_id", new_agency_data, doc_id="new_test_agency_id"
    )

    storage = AgencyConfigFirestoreStorage()
    agency_id = storage.save(new_agency_config)

    assert agency_id is not None


def test_save_existing_agency_config(mock_firestore_client, agency_config_data):
    agency_config = AgencyConfig.model_validate(agency_config_data)
    mock_firestore_client.setup_mock_data("agency_configs", agency_config.agency_id, agency_config_data)

    storage = AgencyConfigFirestoreStorage()
    agency_id = storage.save(agency_config)

    # Assert
    assert agency_id == agency_config.agency_id
    saved_data = mock_firestore_client.collection("agency_configs").document(agency_id).get().to_dict()
    assert saved_data == agency_config.model_dump()
