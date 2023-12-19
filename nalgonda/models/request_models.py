from pydantic import BaseModel, Field


class AgencyMessagePostRequest(BaseModel):
    agency_id: str = Field(..., description="The unique identifier for the agency.")
    message: str = Field(..., description="The message to be sent to the agency.")
    thread_id: str | None = Field(None, description="The identifier for the conversational thread, if applicable.")
