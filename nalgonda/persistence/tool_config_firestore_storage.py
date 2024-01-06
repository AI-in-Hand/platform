from firebase_admin import firestore

from nalgonda.models.tool_config import ToolConfig


class ToolConfigFirestoreStorage:
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection("tool_configs")

    def load_by_user_id(self, user_id: str) -> list[ToolConfig]:
        query = self.collection.where("owner_id", "==", user_id)
        return [ToolConfig.model_validate(document_snapshot.to_dict()) for document_snapshot in query.stream()]

    def load_by_tool_id(self, tool_id: str) -> ToolConfig | None:
        document_snapshot = self.collection.document(tool_id).get()
        if not document_snapshot.exists:
            return None
        return ToolConfig.model_validate(document_snapshot.to_dict())

    def save(self, tool_config: ToolConfig) -> None:
        # Increment version and set as not approved for each new save
        tool_config.version += 1
        tool_config.approved = False

        document_data = tool_config.model_dump()
        if tool_config.tool_id is None:
            # Create a new document and set the tool_id
            document_reference = self.collection.add(document_data)
            tool_config.tool_id = document_reference.id
        self.collection.document(tool_config.tool_id).set(document_data)
