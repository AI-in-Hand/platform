from nalgonda.models.auth import UserInDB


def get_current_active_user_override():
    return UserInDB(username="test_user", hashed_password="hashed_test", disabled=False)
