from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter

from nalgonda.models.tool_config import ToolConfig


class ToolConfigFirestoreStorage:
    def __init__(self):
        self.db = firestore.client()
        self.collection_name = "tool_configs"

    def load_by_owner_id(self, owner_id: str | None = None) -> list[ToolConfig]:
        collection = self.db.collection(self.collection_name)
        query = collection.where(filter=FieldFilter("owner_id", "==", owner_id))
        return [ToolConfig.model_validate(document_snapshot.to_dict()) for document_snapshot in query.stream()]

    def load_by_tool_id(self, tool_id: str) -> ToolConfig | None:
        collection = self.db.collection(self.collection_name)
        document_snapshot = collection.document(tool_id).get()
        if not document_snapshot.exists:
            return None
        return ToolConfig.model_validate(document_snapshot.to_dict())

    def save(self, tool_config: ToolConfig) -> tuple[str, int]:
        collection = self.db.collection(self.collection_name)
        if tool_config.tool_id is None:
            # Create a new document and set the tool_id
            document_reference = collection.add(tool_config.model_dump())[1]
            tool_config.tool_id = document_reference.id
        collection.document(tool_config.tool_id).set(tool_config.model_dump())

        return tool_config.tool_id, tool_config.version
