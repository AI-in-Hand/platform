from pydantic import BaseModel, Field, conlist, field_validator

from backend.models.agent_flow_spec import AgentFlowSpec


class AgencyConfig(BaseModel):
    """Agency configuration model, corresponds to the IFlowConfig type in the frontend"""

    id: str | None = Field(None, description="Unique identifier for the configuration")
    name: str = Field(..., description="Name of the agency")
    description: str = Field("", description="Description of the agency")
    user_id: str | None = Field(None, description="The user ID owning this configuration")
    shared_instructions: str = Field("", description="Agency Manifesto")
    agents: list[str] = Field(default_factory=list, description="List of agent IDs used in the agency chart")
    main_agent: str | None = Field(None, description="The main agent name")
    agency_chart: list[conlist(str, min_length=2, max_length=2)] = Field(  # type: ignore
        default_factory=list,
        description="List representing the agency chart with agent names. "
        "Each item is a pair of names: [sender, receiver]",
    )
    timestamp: str | None = Field(None, description="Timestamp of the last update")

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
        if main_agent not in {agent for sublist in v for agent in sublist}:
            raise ValueError("The main agent must be in the agency chart")

        return v


class AgencyConfigForAPI(AgencyConfig):
    """Agency configuration model for the API"""

    sender: AgentFlowSpec | None = None
    receiver: AgentFlowSpec | None = None
