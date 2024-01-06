from firebase_admin import firestore

from nalgonda.models.agent_config import AgentConfig


class AgentConfigFirestoreStorage:
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection("agent_configs")

    def load(self, agent_id: str) -> AgentConfig | None:
        document_snapshot = self.collection.document(agent_id).get()
        if document_snapshot.exists:
            return AgentConfig.model_validate(document_snapshot)
        return None

    def save(self, agent_config: AgentConfig) -> None:
        document_data = agent_config.model_dump()
        if agent_config.agent_id is None:
            # Create a new document and set the agent_id
            document_reference = self.collection.add(document_data)
            agent_config.agent_id = document_reference.id
        self.collection.document(agent_config.agent_id).set(document_data)
