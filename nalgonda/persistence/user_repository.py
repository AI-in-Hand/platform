from firebase_admin import firestore


class UserRepository:
    def __init__(self):
        self.db = firestore.client()
        self.collection_name = "users"
        self.collection = self.db.collection(self.collection_name)

    def get_user_by_username(self, username: str) -> dict | None:
        user = self.collection.document(username).get()
        if user.exists:
            return user.to_dict()

    def add_or_update_user(self, user: dict):
        self.collection.document(user["username"]).set(user)
