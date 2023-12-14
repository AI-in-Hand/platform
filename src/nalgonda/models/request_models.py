from pydantic import BaseModel


class AgencyMessagePostRequest(BaseModel):
    agency_id: str
    message: str
