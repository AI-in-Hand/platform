import logging

from firebase_admin import firestore
from google.cloud.firestore_v1 import ExistsOption

logger = logging.getLogger(__name__)


class EnvConfigFirestoreStorage:
    def __init__(self):
        """Initialize Firestore client and collection name."""
        self.db = firestore.client()
        self.collection_name = "env_configs"

    def get_config(self, user_id: str) -> dict | None:
        """Fetch environment config based on user_id"""
        logger.info(f"Fetching environment config for user_id: {user_id}")
        collection = self.db.collection(self.collection_name)
        document_snapshot = collection.document(user_id).get()
        return document_snapshot.to_dict() if document_snapshot.exists else None

    def set_config(self, user_id: str, config: dict) -> None:
        """Set environment config based on user_id"""
        logger.info(f"Setting environment config for user_id: {user_id}")
        collection = self.db.collection(self.collection_name)
        collection.document(user_id).set(config)

    def update_config(self, user_id: str, config: dict) -> None:
        logger.info(f"Updating environment config for user_id: {user_id}")
        collection = self.db.collection(self.collection_name)
        collection.document(user_id).update(config, option=ExistsOption(False))
