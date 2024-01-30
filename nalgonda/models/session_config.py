from pydantic import BaseModel, Field


class SessionConfig(BaseModel):
    """Session configuration model"""

    session_id: str = Field(..., description="Unique identifier for the session")
    owner_id: str = Field(..., description="The user ID associated with the session")
    agency_id: str = Field(..., description="Unique identifier for the agency")
