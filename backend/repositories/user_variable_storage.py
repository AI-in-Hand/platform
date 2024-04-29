import logging

from firebase_admin import firestore

logger = logging.getLogger(__name__)


class UserVariableStorage:
    def __init__(self):
        """Initialize Firestore client and collection name."""
        self.db = firestore.client()
        self.collection_name = "user_variables"

    def get_all_variables(self, user_id: str) -> dict | None:
        """Fetch user variables based on user_id"""
        logger.info(f"Fetching user variables for user_id: {user_id}")
        collection = self.db.collection(self.collection_name)
        document_snapshot = collection.document(user_id).get()
        return document_snapshot.to_dict() if document_snapshot.exists else None

    def set_variables(self, user_id: str, variables: dict[str, str]) -> None:
        """Set user variables based on user_id"""
        logger.info(f"Setting user variables for user_id: {user_id}")
        collection = self.db.collection(self.collection_name)
        collection.document(user_id).set(variables)

    def update_variables(self, user_id: str, variables: dict[str, str]) -> None:
        logger.info(f"Updating user variables for user_id: {user_id}")
        collection = self.db.collection(self.collection_name)
        collection.document(user_id).update(variables)
