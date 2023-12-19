from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Config for an agent"""

    id: str | None = None
    role: str
    description: str
    instructions: str
    files_folder: str | None = None
    tools: list[str] = Field(default_factory=list)
