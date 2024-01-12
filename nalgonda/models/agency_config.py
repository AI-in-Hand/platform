from typing import Any

from pydantic import BaseModel, Field, conlist, field_validator


class AgencyConfig(BaseModel):
    """Agency configuration model"""

    agency_id: str = Field(..., description="The agency ID")
    owner_id: str | None = Field(None, description="The user ID owning this agency configuration")
    agency_manifesto: str = Field("Agency Manifesto")
    agents: list[str] = Field(..., description="List of agent IDs used in the agency chart")
    main_agent: str | None = Field(None, description="The main agent name")
    agency_chart: list[conlist(str, min_length=2, max_length=2)] = Field(  # type: ignore
        default_factory=list,
        description="List representing the agency chart with agent names. Each item is a pair of names.",
    )

    def update(self, update_data: dict[str, Any]) -> None:
        for key, value in update_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @field_validator("agency_chart", mode="after")
    @classmethod
    def validate_agency_chart(cls, v, values):
        """Validate the agency chart"""
        if len(v) == 0:
            return v

        # Check if all elements are lists of unique strings
        for element in v:
            if len(set(element)) != len(element):
                raise ValueError("List must be unique")

        # Check if main_agent is set
        main_agent = values.data.get("main_agent")
        if not main_agent:
            raise ValueError("Main agent must be set if agency chart is not empty")

        # Check if the main_agent is in the agency chart
        if main_agent not in [agent for sublist in v for agent in sublist]:
            raise ValueError("The main agent must be in the agency chart")

        return v
