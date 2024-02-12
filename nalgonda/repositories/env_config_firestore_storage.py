import logging

from firebase_admin import firestore

logger = logging.getLogger(__name__)


class EnvConfigFirestoreStorage:
    def __init__(self):
        """Initialize Firestore client and collection name."""
        self.db = firestore.client()
        self.collection_name = "env_configs"
        # TODO: add encryption/decryption

    def get_config(self, owner_id: str) -> dict | None:
        """Fetch environment config based on owner_id"""
        logger.info(f"Fetching environment config for owner_id: {owner_id}")
        collection = self.db.collection(self.collection_name)
        document_snapshot = collection.document(owner_id).get()
        if not document_snapshot.exists:
            return None
        return document_snapshot.to_dict()

    def set_config(self, owner_id: str, config: dict) -> None:
        """Set environment config based on owner_id"""
        logger.info(f"Setting environment config for owner_id: {owner_id}")
        collection = self.db.collection(self.collection_name)
        collection.document(owner_id).set(config)
