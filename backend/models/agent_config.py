from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Config for an agent"""

    id: str | None = Field(None, description="Unique identifier for the configuration")
    user_id: str | None = Field(None, description="The user ID owning this configuration")
    name: str = Field(..., description="Name of the agent (must be globally unique)")
    description: str = Field(..., description="Description of the agent")
    instructions: str = Field(..., description="Instructions for the agent")
    files_folder: str | None = Field(None, description="Folder containing agent-related files")
    skills: list[str] = Field(default_factory=list, description="List of skill names equipped by the agent")
