import json
from unittest.mock import patch

import pytest

from nalgonda.constants import DEFAULT_CONFIG_FILE
from nalgonda.persistence.agency_config_file_storage import AgencyConfigFileStorage
from nalgonda.persistence.agency_config_lock_manager import AgencyConfigLockManager


@pytest.fixture
def mock_config_path(temp_dir):
    """Fixture to patch the _get_config_path method in AgencyConfigFileStorage."""
    agency_id = "test_agency"
    config_path = temp_dir / f"config_{agency_id}.json"

    with patch.object(AgencyConfigFileStorage, "_get_config_path", return_value=config_path):
        yield config_path, agency_id


def test_lock_acquisition_and_release(mock_config_path):
    _, agency_id = mock_config_path
    storage = AgencyConfigFileStorage(agency_id)
    lock = AgencyConfigLockManager.get_lock(agency_id)

    with storage:
        assert lock.locked(), "Lock was not acquired"

    assert not lock.locked(), "Lock was not released"


def test_load_configuration(mock_config_path):
    config_path, agency_id = mock_config_path
    config_data = {"key": "value"}
    config_path.write_text(json.dumps(config_data))

    storage = AgencyConfigFileStorage(agency_id)
    with storage:
        loaded_config = storage.load()

    assert loaded_config == config_data, "Loaded configuration does not match expected data"


def test_save_configuration(mock_config_path):
    config_path, agency_id = mock_config_path
    new_config = {"new_key": "new_value"}

    storage = AgencyConfigFileStorage(agency_id)
    with storage:
        storage.save(new_config)

    assert config_path.exists(), "Configuration file was not created"
    with open(config_path) as file:
        saved_data = json.load(file)
    assert saved_data == new_config, "Saved data does not match"


def test_default_configuration_used(mock_config_path):
    config_path, agency_id = mock_config_path

    with open(DEFAULT_CONFIG_FILE) as file:
        default_config = json.load(file)

    # Ensure the specific config file does not exist to trigger default config usage
    if config_path.exists():
        config_path.unlink()

    storage = AgencyConfigFileStorage(agency_id)
    with storage:
        loaded_config = storage.load()

    assert loaded_config == default_config, "Default configuration was not used"
