from datetime import UTC, datetime

from pydantic import BaseModel, Field

from backend.models.skill_config import SkillConfig
from backend.settings import settings


class CodeExecutionConfig(BaseModel):
    work_dir: str | None = Field(None, description="Working directory for code execution")
    use_docker: bool = Field(False, description="Whether to use Docker for code execution")


class AgentConfig(BaseModel):
    """Config for an agent, corresponds to the IAgentConfig in the frontend"""

    name: str = Field(..., description="Name of the agent")
    system_message: str = Field("", description="System message")
    model: str = Field(settings.gpt_small_model, description="Model for the agent to use")
    code_execution_config: CodeExecutionConfig = Field(
        CodeExecutionConfig(), description="Configuration for code execution"
    )


class AgentFlowSpec(BaseModel):
    """Config for an agent"""

    id: str | None = Field(None, description="Unique identifier for the configuration")
    config: AgentConfig = Field(..., description="Agent configuration")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(), description="Timestamp of the last update"
    )
    skills: list[str] = Field(  # type: ignore
        default_factory=list, description="List of skill titles"
    )
    description: str = Field("", description="Description of the agent")
    user_id: str | None = Field(None, description="The user ID owning this configuration")


class AgentFlowSpecForAPI(AgentFlowSpec):
    """Config for an agent, corresponds to the IAgentFlowSpec in the frontend"""

    id: str | None = Field(None, description="Unique identifier for the configuration")
    skills: list[SkillConfig] = Field(  # type: ignore
        default_factory=list, description="List of skill configurations equipped by the agent"
    )
