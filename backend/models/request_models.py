from pydantic import BaseModel, Field


class MessagePostRequest(BaseModel):
    """Request model for sending a message to the User Proxy of the given agency.
    Corresponds to the IMessage interface in the frontend."""

    agency_id: str = Field(..., description="The unique identifier for the agency.")
    session_id: str = Field(..., description="The identifier for the conversational thread.")
    content: str = Field(..., description="The message to be sent to the agency.")


class SkillExecutePostRequest(BaseModel):
    id: str = Field(..., description="The unique identifier for the skill.")
    user_prompt: str = Field(..., description="The user prompt to extract parameters from.")
