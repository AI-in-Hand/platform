import json
from pathlib import Path

from nalgonda.constants import CONFIG_FILE_BASE, DEFAULT_CONFIG_FILE
from nalgonda.persistence.agency_config_lock_manager import AgencyConfigLockManager
from nalgonda.persistence.agency_config_storage_interface import AgencyConfigStorageInterface


class AgencyConfigFileStorage(AgencyConfigStorageInterface):
    """
    A thread-safe context manager for handling agency-specific configuration files.

    This class ensures that file operations on configuration files are managed
    in a thread-safe manner using locks. Each agency identified by its unique ID
    gets its own lock to prevent concurrent access issues.
    """

    def __init__(self, agency_id: str):
        self.config_file_path = self._get_config_path(agency_id)
        self.lock = None
        self.agency_id = agency_id

    def __enter__(self):
        """
        Enters the runtime context and acquires the lock for the agency file.

        If the specific agency configuration file does not exist, it falls back
        to a default configuration file.

        Returns:
            self: An instance of AgencyConfigFileStorage.
        """
        self.lock = AgencyConfigLockManager.get_lock(self.agency_id)
        self.lock.acquire()
        if not self.config_file_path.is_file():
            self._create_default_config()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the runtime context and releases the lock for the agency file.
        """
        self.lock.release()

    def load(self):
        """
        Loads the configuration from the agency file.

        Returns:
            dict: The loaded configuration data.
        """
        with self.config_file_path.open() as file:
            return json.load(file)

    def save(self, data):
        """
        Saves the provided data to the agency file.

        Args:
            data (dict): The configuration data to be saved.
        """
        with self.config_file_path.open("w") as file:
            json.dump(data, file, indent=2)

    def _create_default_config(self):
        """
        Creates a new configuration file based on the default configuration.
        """
        with DEFAULT_CONFIG_FILE.open() as file:
            config = json.load(file)
        self.save(config)

    @staticmethod
    def _get_config_path(agency_id: str) -> Path:
        """
        Generates the path for the agency configuration file.

        Args:
            agency_id (str): The unique identifier for the agency.

        Returns:
            Path: The path object for the agency configuration file.
        """
        return CONFIG_FILE_BASE.with_name(f"config_{agency_id}.json")
