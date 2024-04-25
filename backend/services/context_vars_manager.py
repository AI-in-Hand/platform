"""
A class to manage context variables using ContextVar.

No need to use:
# module-level:
context_vars = ContextVar('context_vars')
# in the API routers:
context_vars_old = context_vars.get()
context_vars_old.update({'user_id': user_id})
context_vars.set(context_vars_old)

# It all turns into one line when using the ContextEnvVarsManager:
ContextEnvVarsManager.set('user_id', user_id)
"""

from contextvars import ContextVar
from typing import Any


class ContextEnvVarsManager:
    """A class to manage context variables using ContextVar."""

    context_vars: ContextVar = ContextVar("context_vars")

    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """Set an environment variable."""
        try:
            context_vars_old = cls.context_vars.get()
        except LookupError:
            context_vars_old = {}
        context_vars_old.update({key: value})
        cls.context_vars.set(context_vars_old)

    @classmethod
    def get(cls, key: str) -> Any:
        """Get an environment variable."""
        try:
            context_vars_dict = cls.context_vars.get()
            return context_vars_dict.get(key)
        except LookupError:
            return None

    @classmethod
    def get_all(cls) -> dict:
        """Get all context variables."""
        try:
            return cls.context_vars.get()
        except LookupError:
            return {}
