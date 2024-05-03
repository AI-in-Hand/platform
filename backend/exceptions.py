# exceptions.py - Custom exceptions for the AI in Hand Platform
# This file is reserved for custom exception classes.


class UnsetVariableError(ValueError):
    """Exception raised when a required variable is unset or not defined."""

    def __init__(self, key: str):
        message = f"Variable {key} is not set. Please set it first."
        super().__init__(message)


class HandledValidationError(ValueError):
    """A base class for all custom validation errors that we handle in the dedicated exception handler."""

    def __init__(self, message: str):
        super().__init__(message)


class ValidationErrorEmptyFlows(HandledValidationError):
    """Exception raised when the flows list is empty."""

    def __init__(self):
        message = "Please add at least one agent"
        super().__init__(message)


class ValidationErrorSameSenderReceiver(HandledValidationError):
    """Exception raised when the same agent is set as both sender and receiver."""

    def __init__(self):
        message = "Cannot set the same agent as both sender and receiver"
        super().__init__(message)


class ValidationErrorMissingSender(HandledValidationError):
    """Exception raised when the sender agent is not set."""

    def __init__(self):
        message = "Sender agent is required"
        super().__init__(message)


class ValidationErrorMissingReceiver(HandledValidationError):
    """Exception raised when the receiver agent is not set."""

    def __init__(self):
        message = "Receiver agent is required"
        super().__init__(message)
