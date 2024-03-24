from firebase_admin import firestore
from google.cloud.firestore_v1 import FieldFilter

from nalgonda.models.skill_config import SkillConfig


class SkillConfigFirestoreStorage:
    def __init__(self):
        self.db = firestore.client()
        self.collection_name = "skill_configs"

    def load_by_owner_id(self, owner_id: str | None = None) -> list[SkillConfig]:
        collection = self.db.collection(self.collection_name)
        query = collection.where(filter=FieldFilter("owner_id", "==", owner_id))
        return [SkillConfig.model_validate(document_snapshot.to_dict()) for document_snapshot in query.stream()]

    def load_by_id(self, id_: str) -> SkillConfig | None:
        collection = self.db.collection(self.collection_name)
        document_snapshot = collection.document(id_).get()
        if not document_snapshot.exists:
            return None
        return SkillConfig.model_validate(document_snapshot.to_dict())

    def save(self, skill_config: SkillConfig) -> tuple[str, int]:
        collection = self.db.collection(self.collection_name)
        if skill_config.id is None:
            # Create a new document and set the id
            document_reference = collection.add(skill_config.model_dump())[1]
            skill_config.id = document_reference.id
        collection.document(skill_config.id).set(skill_config.model_dump())

        return skill_config.id, skill_config.version
