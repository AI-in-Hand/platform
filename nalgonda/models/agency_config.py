from typing import Any

from pydantic import BaseModel, Field


class AgencyConfig(BaseModel):
    """Agency configuration model"""

    agency_id: str = Field(..., description="The agency ID")
    owner_id: str | None = Field(None, description="The user ID owning this agency configuration")
    agency_manifesto: str = Field("Agency Manifesto")
    agents: list[str] = Field(..., description="List of agent IDs used in the agency chart")
    agency_chart: list[str | list[str]] = Field(..., description="List representing the agency chart with agent names")

    def update(self, update_data: dict[str, Any]) -> None:
        for key, value in update_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
