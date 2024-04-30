from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter

from backend.models.session_config import SessionConfig


class SessionConfigStorage:
    def __init__(self):
        self.db = firestore.client()
        self.collection_name = "session_configs"

    def load_by_user_id(self, user_id: str | None = None) -> list[SessionConfig]:
        collection = self.db.collection(self.collection_name)
        query = collection.where(filter=FieldFilter("user_id", "==", user_id))
        return [SessionConfig.model_validate(document_snapshot.to_dict()) for document_snapshot in query.stream()]

    def load_by_agency_id(self, agency_id: str) -> list[SessionConfig]:
        collection = self.db.collection(self.collection_name)
        query = collection.where(filter=FieldFilter("agency_id", "==", agency_id))
        return [SessionConfig.model_validate(document_snapshot.to_dict()) for document_snapshot in query.stream()]

    def load_by_id(self, session_id: str) -> SessionConfig | None:
        collection = self.db.collection(self.collection_name)
        document_snapshot = collection.document(session_id).get()
        return SessionConfig.model_validate(document_snapshot.to_dict()) if document_snapshot.exists else None

    def save(self, session_config: SessionConfig) -> None:
        collection = self.db.collection(self.collection_name)
        collection.document(session_config.id).set(session_config.model_dump())

    def update(self, session_id: str, fields: dict[str, str]) -> None:
        """Update the session with the given fields."""
        collection = self.db.collection(self.collection_name)
        collection.document(session_id).update(fields)

    def delete(self, session_id: str) -> None:
        collection = self.db.collection(self.collection_name)
        collection.document(session_id).delete()

    def delete_by_agency_id(self, agency_id: str) -> None:
        sessions = self.load_by_agency_id(agency_id)
        for session in sessions:
            self.delete(session.id)
