from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter

from backend.models.agent_flow_spec import AgentFlowSpec


class AgentFlowSpecFirestoreStorage:
    def __init__(self):
        self.db = firestore.client()
        self.collection_name = "agent_configs"

    def load_by_user_id(self, user_id: str | None = None) -> list[AgentFlowSpec]:
        collection = self.db.collection(self.collection_name)
        query = collection.where(filter=FieldFilter("user_id", "==", user_id))
        return [AgentFlowSpec.model_validate(document_snapshot.to_dict()) for document_snapshot in query.stream()]

    def load_by_id(self, id_: str) -> AgentFlowSpec | None:
        collection = self.db.collection(self.collection_name)
        document_snapshot = collection.document(id_).get()
        if not document_snapshot.exists:
            return None
        return AgentFlowSpec.model_validate(document_snapshot.to_dict())

    def save(self, agent_flow_spec: AgentFlowSpec) -> str:
        """Save the agent configuration to the Firestore.
        If the agent id is not set, it will create a new document and set the agent id.
        Returns the agent id."""
        collection = self.db.collection(self.collection_name)
        if agent_flow_spec.id is None:
            # Create a new document and set the id
            document_reference = collection.add(agent_flow_spec.model_dump())[1]
            agent_flow_spec.id = document_reference.id

        collection.document(agent_flow_spec.id).set(agent_flow_spec.model_dump())
        return agent_flow_spec.id