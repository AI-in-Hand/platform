from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter

from nalgonda.models.agency_config import AgencyConfig


class AgencyConfigFirestoreStorage:
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection("agency_configs")

    def load_by_owner_id(self, owner_id: str | None = None) -> list[AgencyConfig]:
        query = self.collection.where(filter=FieldFilter("owner_id", "==", owner_id))
        return [AgencyConfig.model_validate(document_snapshot.to_dict()) for document_snapshot in query.stream()]

    def load_by_agency_id(self, agency_id: str) -> AgencyConfig | None:
        document_ref = self.collection.document(agency_id)
        agency_config_snapshot = document_ref.get()
        if agency_config_snapshot.exists:
            return AgencyConfig.model_validate(agency_config_snapshot.to_dict())
        return None

    def save(self, agency_config: AgencyConfig) -> str:
        """Save the agency configuration to the Firestore.
        If the agency_id is not set, it will create a new document and set the agency_id.
        Returns the agency_id."""
        if agency_config.agency_id is None:
            # Create a new document and set the agency_id
            document_reference = self.collection.add(agency_config.model_dump())[1]
            agency_config.agency_id = document_reference.id

        self.collection.document(agency_config.agency_id).set(agency_config.model_dump())
        return agency_config.agency_id
