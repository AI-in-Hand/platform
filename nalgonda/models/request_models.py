from pydantic import BaseModel, Field


class SessionPostRequest(BaseModel):
    agency_id: str = Field(..., description="The unique identifier for the agency.")


class SessionMessagePostRequest(BaseModel):
    agency_id: str = Field(..., description="The unique identifier for the agency.")
    session_id: str = Field(..., description="The identifier for the conversational thread.")
    message: str = Field(..., description="The message to be sent to the agency.")
