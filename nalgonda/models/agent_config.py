from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Config for an agent"""

    agent_id: str | None = Field(default=None, description="Unique identifier for the agent configuration")
    role: str = Field(..., description="Role of the agent within an agency")
    owner_id: str = Field(..., description="The user ID owning this agent configuration")
    description: str = Field(..., description="Description of the agent")
    instructions: str = Field(..., description="Instructions for the agent")
    files_folder: str = Field(default=None, description="Folder containing agent-related files")
    tools: list[str] = Field(default_factory=list, description="List of tool names equipped by the agent")
