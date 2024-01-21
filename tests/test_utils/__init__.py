from nalgonda.models.auth import UserInDB
from tests.test_utils.constants import TEST_USER_ID


def get_current_active_user_override():
    return UserInDB(id=TEST_USER_ID, username=TEST_USER_ID, hashed_password="hashed_password_test", disabled=False)


def get_current_superuser_override():
    return UserInDB(
        id=TEST_USER_ID,
        username=TEST_USER_ID,
        hashed_password="hashed_password_test",
        disabled=False,
        is_superuser=True,
    )
