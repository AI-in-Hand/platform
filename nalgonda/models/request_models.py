from pydantic import BaseModel, Field


class ThreadPostRequest(BaseModel):
    agency_id: str = Field(..., description="The unique identifier for the agency.")


class AgencyMessagePostRequest(BaseModel):
    agency_id: str = Field(..., description="The unique identifier for the agency.")
    message: str = Field(..., description="The message to be sent to the agency.")
    thread_id: str = Field(..., description="The identifier for the conversational thread.")
