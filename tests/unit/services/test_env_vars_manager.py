from contextvars import ContextVar

import pytest

from nalgonda.services.env_vars_manager import ContextEnvVarsManager
from tests.test_utils import TEST_USER_ID


@pytest.fixture(autouse=True)
def reset_env_vars():
    # Reset the context variable to its default state before each test
    ContextEnvVarsManager.environment_vars = ContextVar("environment_vars")
    yield
    # No teardown needed, but you could add one if necessary


def test_set_method():
    # Test setting a new environment variable
    ContextEnvVarsManager.set("new_key", "new_value")
    assert ContextEnvVarsManager.get("new_key") == "new_value"


def test_get_method_success():
    ContextEnvVarsManager.set("owner_id", TEST_USER_ID)
    assert ContextEnvVarsManager.get("owner_id") == TEST_USER_ID


def test_get_method_no_key():
    ContextEnvVarsManager.set("some_key", "some_value")
    assert ContextEnvVarsManager.get("nonexistent_key") is None


def test_get_all_method_success():
    ContextEnvVarsManager.set("owner_id", TEST_USER_ID)
    assert ContextEnvVarsManager.get_all() == {"owner_id": TEST_USER_ID}


def test_get_all_method_empty():
    assert ContextEnvVarsManager.get_all() is None


# Optional: Test for edge cases like setting None or empty strings
def test_set_method_edge_cases():
    ContextEnvVarsManager.set("", "empty_key")
    ContextEnvVarsManager.set("none_value", None)
    assert ContextEnvVarsManager.get("") == "empty_key"
    assert ContextEnvVarsManager.get("none_value") is None
