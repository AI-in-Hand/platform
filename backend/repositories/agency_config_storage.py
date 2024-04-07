from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter

from backend.models.agency_config import AgencyConfig


class AgencyConfigStorage:
    def __init__(self):
        self.db = firestore.client()
        self.collection_name = "agency_configs"

    def load_by_user_id(self, user_id: str | None = None) -> list[AgencyConfig]:
        collection = self.db.collection(self.collection_name)
        query = collection.where(filter=FieldFilter("user_id", "==", user_id))
        return [AgencyConfig.model_validate(document_snapshot.to_dict()) for document_snapshot in query.stream()]

    def load_by_id(self, id_: str) -> AgencyConfig | None:
        collection = self.db.collection(self.collection_name)
        document_snapshot = collection.document(id_).get()
        return AgencyConfig.model_validate(document_snapshot.to_dict()) if document_snapshot.exists else None

    def save(self, agency_config: AgencyConfig) -> str:
        """Save the agency configuration to the Firestore.
        If the id is not set, it will create a new document and set the id.
        Returns the id."""
        collection = self.db.collection(self.collection_name)
        if agency_config.id is None:
            # Create a new document and set the id
            document_reference = collection.add(agency_config.model_dump())[1]
            agency_config.id = document_reference.id

        collection.document(agency_config.id).set(agency_config.model_dump())
        return agency_config.id

    def delete(self, id_: str) -> None:
        collection = self.db.collection(self.collection_name)
        collection.document(id_).delete()
