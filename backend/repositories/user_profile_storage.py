import logging

from firebase_admin import firestore

logger = logging.getLogger(__name__)


class UserProfileStorage:
    def __init__(self):
        """Initialize Firestore client and collection name."""
        self.db = firestore.client()
        self.collection_name = "user_profiles"

    def get_profile(self, user_id: str) -> dict | None:
        """Fetch user profile data based on user_id"""
        logger.info(f"Fetching user profile data for user_id: {user_id}")
        collection = self.db.collection(self.collection_name)
        document_snapshot = collection.document(user_id).get()
        return document_snapshot.to_dict() if document_snapshot.exists else None

    def update_profile(self, user_id: str, fields: dict[str, str]) -> None:
        """Set user profile data based on user_id"""
        logger.info(f"Updating user profile data for user_id: {user_id}")
        collection = self.db.collection(self.collection_name)
        collection.document(user_id).set(fields)
