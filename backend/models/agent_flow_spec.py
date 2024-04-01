from typing import Literal

from pydantic import BaseModel, Field, conlist

from backend.models.skill_config import SkillConfig


class CodeExecutionConfig(BaseModel):
    work_dir: str | None = Field(None, description="Working directory for code execution")
    use_docker: bool = Field(False, description="Whether to use Docker for code execution")


class AgentConfig(BaseModel):
    """Config for an agent, corresponds to IAgentConfig in the frontend"""

    name: str = Field(..., description="Name of the agent")
    system_message: str = Field("", description="System message")
    code_execution_config: CodeExecutionConfig = Field(
        CodeExecutionConfig(), description="Configuration for code execution"
    )


class AgentFlowSpec(BaseModel):
    """Config for an agent"""

    id: str | None = Field(None, description="Unique identifier for the configuration")
    type: Literal["assistant", "userproxy", "groupchat"] = Field("userproxy", description="Type of the agent")
    config: AgentConfig = Field(..., description="Agent configuration")
    timestamp: str | None = Field(None, description="Timestamp of the last update")
    skills: conlist(str, max_length=10) = Field(  # type: ignore
        default_factory=list, description="List of skill titles"
    )
    description: str = Field("", description="Description of the agent")
    user_id: str | None = Field(None, description="The user ID owning this configuration")


class AgentFlowSpecForAPI(AgentFlowSpec):
    """Config for an agent, corresponds to IAgentFlowSpec in the frontend"""

    skills: conlist(SkillConfig, max_length=10) = Field(  # type: ignore
        default_factory=list, description="List of skill configurations equipped by the agent"
    )
