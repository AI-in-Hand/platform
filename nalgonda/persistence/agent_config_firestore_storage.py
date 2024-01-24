from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter

from nalgonda.models.agent_config import AgentConfig


class AgentConfigFirestoreStorage:
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection("agent_configs")

    def load_by_user_id(self, user_id: str) -> list[AgentConfig]:
        query = self.collection.where(filter=FieldFilter("owner_id", "==", user_id))
        return [AgentConfig.model_validate(document_snapshot.to_dict()) for document_snapshot in query.stream()]

    def load_by_agent_id(self, agent_id: str) -> AgentConfig | None:
        document_snapshot = self.collection.document(agent_id).get()
        if not document_snapshot.exists:
            return None
        return AgentConfig.model_validate(document_snapshot.to_dict())

    def save(self, agent_config: AgentConfig) -> str:
        """Save the agent configuration to the firestore.
        If the agent_id is not set, it will create a new document and set the agent_id.
        Returns the agent_id."""
        if agent_config.agent_id is None:
            # Create a new document and set the agent_id
            document_reference = self.collection.add(agent_config.model_dump())[0]
            agent_config.agent_id = document_reference.id

        self.collection.document(agent_config.agent_id).set(agent_config.model_dump())
        return agent_config.agent_id
