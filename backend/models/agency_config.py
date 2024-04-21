from pydantic import BaseModel, Field, conlist, field_validator

from backend.models.agent_flow_spec import AgentFlowSpecForAPI


class AgencyConfig(BaseModel):
    """Agency configuration model"""

    id: str | None = Field(None, description="Unique identifier for the configuration")
    name: str = Field(..., description="Name of the agency")
    description: str = Field("", description="Description of the agency")
    user_id: str | None = Field(None, description="The user ID owning this configuration")
    shared_instructions: str = Field("", description="Agency Manifesto")  # TODO: support in the frontend
    agents: list[str] = Field(default_factory=list, description="List of agent IDs used in the agency chart")
    main_agent: str = Field(..., description="The main agent name")
    agency_chart: dict[str, conlist(str, min_length=2, max_length=2)] = Field(  # type: ignore
        default_factory=dict,
        description="Dict representing the agency chart with agent names. "
        "Each item value is a pair of names: [sender, receiver]",
    )
    timestamp: str | None = Field(None, description="Timestamp of the last update")

    @field_validator("main_agent", mode="before", check_fields=True)
    @classmethod
    def validate_main_agent(cls, v, values):  # noqa: ARG003
        """Validate the main agent is not None"""
        if not v:
            raise ValueError("Please add at least one agent")
        return v

    @field_validator("agency_chart", mode="after")
    @classmethod
    def validate_agency_chart(cls, v, values):
        """Validate the agency chart"""
        if len(v) == 0:
            return v

        # Check if all elements are lists of unique strings
        for chart_row in v.values():
            if len(set(chart_row)) != len(chart_row):
                raise ValueError("Chart row must be unique")

        # Check if the main_agent is in the agency chart
        main_agent = values.data.get("main_agent")
        if main_agent not in {agent for sublist in v.values() for agent in sublist}:
            raise ValueError("The main agent must be in the agency chart")

        return v


class AgencyConfigForAPI(BaseModel):
    """Agency configuration model for the API, corresponds to the IFlowConfig type in the frontend"""

    id: str | None = Field(None, description="Unique identifier for the configuration")
    sender: AgentFlowSpecForAPI | None = None
    receiver: AgentFlowSpecForAPI | None = None

    name: str = Field(..., description="Name of the agency")
    description: str = Field("", description="Description of the agency")
    user_id: str | None = Field(None, description="The user ID owning this configuration")
    shared_instructions: str = Field("", description="Agency Manifesto")
    timestamp: str | None = Field(None, description="Timestamp of the last update")
