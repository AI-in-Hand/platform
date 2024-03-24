from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter

from backend.models.session_config import SessionConfig


class SessionConfigFirestoreStorage:
    def __init__(self):
        self.db = firestore.client()
        self.collection_name = "session_configs"

    def load_by_owner_id(self, owner_id: str | None = None) -> list[SessionConfig]:
        collection = self.db.collection(self.collection_name)
        query = collection.where(filter=FieldFilter("owner_id", "==", owner_id))
        return [SessionConfig.model_validate(document_snapshot.to_dict()) for document_snapshot in query.stream()]

    def load_by_session_id(self, session_id: str) -> SessionConfig | None:
        collection = self.db.collection(self.collection_name)
        document_snapshot = collection.document(session_id).get()
        if not document_snapshot.exists:
            return None
        return SessionConfig.model_validate(document_snapshot.to_dict())

    def save(self, session_config: SessionConfig) -> None:
        collection = self.db.collection(self.collection_name)
        collection.document(session_config.session_id).set(session_config.model_dump())
