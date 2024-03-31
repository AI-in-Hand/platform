from pydantic import BaseModel, Field


class SessionConfig(BaseModel):
    """Session configuration model"""

    session_id: str = Field(..., description="Unique identifier for the session")
    user_id: str = Field(..., description="The user ID associated with the session")
    agency_id: str = Field(..., description="Unique identifier for the agency")
    created_at: int = Field(..., description="The timestamp at which the session was created")
