import logging

from firebase_admin import firestore

logger = logging.getLogger(__name__)


class UserSecretStorage:
    def __init__(self):
        """Initialize Firestore client and collection name."""
        self.db = firestore.client()
        self.collection_name = "user_secrets"

    def get_all_secrets(self, user_id: str) -> dict | None:
        """Fetch environment config based on user_id"""
        logger.info(f"Fetching user secrets for user_id: {user_id}")
        collection = self.db.collection(self.collection_name)
        document_snapshot = collection.document(user_id).get()
        return document_snapshot.to_dict() if document_snapshot.exists else None

    def set_secrets(self, user_id: str, config: dict) -> None:
        """Set environment config based on user_id"""
        logger.info(f"Setting user secrets for user_id: {user_id}")
        collection = self.db.collection(self.collection_name)
        collection.document(user_id).set(config)

    def update_secrets(self, user_id: str, config: dict) -> None:
        logger.info(f"Updating user secrets for user_id: {user_id}")
        collection = self.db.collection(self.collection_name)
        collection.document(user_id).update(config)
