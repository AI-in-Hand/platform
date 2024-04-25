from backend.models.auth import User
from backend.services.context_vars_manager import ContextEnvVarsManager
from tests.testing_utils.constants import TEST_USER_EMAIL, TEST_USER_ID


def get_current_user_override():
    return User(
        id=TEST_USER_ID,
        email=TEST_USER_EMAIL,
    )


def get_current_superuser_override():
    return User(
        id=TEST_USER_ID,
        email=TEST_USER_EMAIL,
        is_superuser=True,
    )


def reset_context_vars():
    for var in ContextEnvVarsManager.get_all():
        ContextEnvVarsManager.set(var, None)
