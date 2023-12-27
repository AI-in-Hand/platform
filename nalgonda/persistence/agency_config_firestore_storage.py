import json
from typing import Any

from firebase_admin import firestore

from nalgonda.constants import DEFAULT_CONFIG_FILE
from nalgonda.persistence.agency_config_storage_interface import AgencyConfigStorageInterface


class AgencyConfigFirestoreStorage(AgencyConfigStorageInterface):
    def __init__(self, agency_id: str):
        self.db = firestore.client()
        self.agency_id = agency_id
        self.collection_name = "agency_configs"
        self.document = self.db.collection(self.collection_name).document(agency_id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # No special action needed on exiting the context.
        pass

    def load(self):
        db_config = self.document.get().to_dict()
        if not db_config:
            db_config = self._create_default_config()
        return db_config

    def save(self, data: dict[str, Any]):
        self.document.set(data)

    def _create_default_config(self) -> dict[str, Any]:
        """Creates a default config for the agency and saves it to the database."""
        with DEFAULT_CONFIG_FILE.open() as file:
            config = json.load(file)
        self.save(config)
        return config
