from firebase_admin import firestore

from nalgonda.models.auth import UserInDB


class UserRepository:
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection("users")

    def get_user_by_id(self, user_id: str) -> dict | None:
        user = self.collection.document(user_id).get()
        if user.exists:
            return user.to_dict()

    def update_user(self, user: UserInDB):
        self.collection.document(user.id).set(user)
