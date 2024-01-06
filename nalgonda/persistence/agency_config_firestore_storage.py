from typing import Any

from firebase_admin import firestore

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

    def load(self) -> dict[str, Any] | None:
        db_config = self.document.get().to_dict()
        return db_config

    def save(self, data: dict[str, Any]):
        self.document.set(data)
