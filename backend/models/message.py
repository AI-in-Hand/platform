from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Request model for sending a message to the User Proxy of the given agency.
    Corresponds to the IMessage interface in the frontend."""

    id: str | None = Field(None, description="The unique identifier for the message.")
    agency_id: str = Field(..., description="The unique identifier for the agency.")
    session_id: str = Field(..., description="The identifier for the conversational thread.")
    role: Literal["user", "assistant"] = Field("user", description="The role of the sender of the message.")
    content: str = Field(..., description="The message to be sent to the agency.")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(), description="The timestamp when the message was created."
    )
