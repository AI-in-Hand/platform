from nalgonda.models.auth import User
from tests.test_utils.constants import TEST_USER_ID


def get_current_active_user_override():
    return User(id=TEST_USER_ID, username=TEST_USER_ID, disabled=False)


def get_current_superuser_override():
    return User(
        id=TEST_USER_ID,
        username=TEST_USER_ID,
        disabled=False,
        is_superuser=True,
    )
