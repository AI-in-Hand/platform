from pydantic import BaseModel, Field

from backend.models.agency_config import AgencyConfigForAPI


class SessionConfig(BaseModel):
    """Session configuration model"""

    id: str = Field(..., description="Unique identifier for the session")
    user_id: str = Field(..., description="The user ID associated with the session")
    agency_id: str = Field(..., description="Unique identifier for the agency")
    timestamp: str = Field(..., description="The timestamp at which the session was created")


class SessionConfigForAPI(SessionConfig):
    """Session configuration model for the API. Corresponds to the IChatSession type in the frontend"""

    flow_config: AgencyConfigForAPI = Field(..., description="The flow (agency) configuration for the session")
