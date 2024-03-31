"""
A class to manage environment variables using ContextVar.

No need to use:
# module-level:
environment_vars = ContextVar('environment_vars')
# in the API routers:
environment_vars_old = environment_vars.get()
environment_vars_old.update({'user_id': user_id})
environment_vars.set(environment_vars_old)

# It all turns into one line when using the ContextEnvVarsManager:
ContextEnvVarsManager.set('user_id', user_id)
"""

from contextvars import ContextVar
from typing import Any


class ContextEnvVarsManager:
    """A class to manage environment variables using ContextVar."""

    environment_vars: ContextVar = ContextVar("environment_vars")

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """Set an environment variable."""
        try:
            environment_vars_old = cls.environment_vars.get()
        except LookupError:
            environment_vars_old = {}
        environment_vars_old.update({key: value})
        cls.environment_vars.set(environment_vars_old)

    @classmethod
    def get(cls, key: str) -> Any:
        """Get an environment variable."""
        try:
            env_vars_dict = cls.environment_vars.get()
            return env_vars_dict.get(key)
        except LookupError:
            return None

    @classmethod
    def get_all(cls) -> dict | None:
        """Get all environment variables."""
        try:
            return cls.environment_vars.get()
        except LookupError:
            return None
