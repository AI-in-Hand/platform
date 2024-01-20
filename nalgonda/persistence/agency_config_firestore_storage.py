import json

from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter

from nalgonda.constants import DEFAULT_AGENCY_CONFIG_FILE
from nalgonda.models.agency_config import AgencyConfig


class AgencyConfigFirestoreStorage:
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection("agency_configs")

    def load_by_user_id(self, user_id: str) -> list[AgencyConfig]:
        query = self.collection.where(filter=FieldFilter("owner_id", "==", user_id))
        return [AgencyConfig.model_validate(document_snapshot.to_dict()) for document_snapshot in query.stream()]

    def load_by_agency_id(self, agency_id: str) -> AgencyConfig | None:
        document_ref = self.collection.document(agency_id)
        agency_config_snapshot = document_ref.get()
        if agency_config_snapshot.exists:
            return AgencyConfig.model_validate(agency_config_snapshot.to_dict())
        return None

    def load_or_create(self, agency_id: str) -> AgencyConfig:
        agency_config = self.load_by_agency_id(agency_id)
        if agency_config is None:
            with open(DEFAULT_AGENCY_CONFIG_FILE) as default_config_file:
                config_data = json.load(default_config_file)
            config_data["agency_id"] = agency_id
            agency_config = AgencyConfig.model_validate(config_data)
            self.save(agency_id, agency_config)
        return agency_config

    def save(self, agency_id: str, agency_config: AgencyConfig) -> None:
        document_data = agency_config.model_dump()
        document_ref = self.collection.document(agency_id)
        document_ref.set(document_data)
