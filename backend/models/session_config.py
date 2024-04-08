from pydantic import BaseModel, Field


class SessionConfig(BaseModel):
    """Session configuration model. Corresponds to the IChatSession type in the frontend"""

    id: str = Field(..., description="Unique identifier for the session")
    user_id: str = Field(..., description="The user ID associated with the session")
    agency_id: str = Field(..., description="Unique identifier for the agency")
    timestamp: str = Field(..., description="The timestamp at which the session was created")
