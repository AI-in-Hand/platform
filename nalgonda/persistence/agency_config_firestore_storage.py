import json

from firebase_admin import firestore

from nalgonda.constants import DEFAULT_AGENCY_CONFIG_FILE
from nalgonda.models.agency_config import AgencyConfig


class AgencyConfigFirestoreStorage:
    def __init__(self, agency_id: str):
        self.db = firestore.client()
        self.agency_id = agency_id
        self.collection_name = "agency_configs"
        self.document_ref = self.db.collection(self.collection_name).document(agency_id)

    def load(self) -> AgencyConfig | None:
        agency_config_snapshot = self.document_ref.get()
        if agency_config_snapshot.exists:
            return AgencyConfig.model_validate(agency_config_snapshot.to_dict())
        return None

    def load_or_create(self) -> AgencyConfig:
        agency_config = self.load()
        if agency_config is None:
            with open(DEFAULT_AGENCY_CONFIG_FILE) as default_config_file:
                config_data = json.load(default_config_file)
            config_data["agency_id"] = self.agency_id
            agency_config = AgencyConfig.model_validate(config_data)
            self.save(agency_config)
        return agency_config

    def save(self, agency_config: AgencyConfig) -> None:
        document_data = agency_config.model_dump()
        self.document_ref.set(document_data)
