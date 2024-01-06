from firebase_admin import firestore

from nalgonda.models.agent_config import AgentConfig


class AgentConfigFirestoreStorage:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.db = firestore.client()
        self.collection = self.db.collection("agent_configs")

    def load(self) -> AgentConfig | None:
        document_snapshot = self.collection.document(self.agent_id).get()
        if document_snapshot.exists:
            return AgentConfig.model_validate(document_snapshot)
        return None

    def save(self, agent_config: AgentConfig) -> None:
        document_data = agent_config.model_dump()
        self.collection.document(self.agent_id).set(document_data)
