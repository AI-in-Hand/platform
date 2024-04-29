# exceptions.py - Custom exceptions for the AI in Hand Platform
# This file is reserved for custom exception classes.


class UnsetVariableError(ValueError):
    """Exception raised when a required variable is unset or not defined."""

    def __init__(self, key: str):
        message = f"Variable {key} is not set. Please set it first."
        super().__init__(message)
