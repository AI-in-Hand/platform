from typing import Literal

from pydantic import BaseModel, Field


class CodeExecutionConfig(BaseModel):
    work_dir: str | None = Field(None, description="Working directory for code execution")
    use_docker: bool = Field(False, description="Whether to use Docker for code execution")


class AgentConfig(BaseModel):
    """Config for an agent, corresponds to IAgentConfig in the frontend"""

    name: str = Field(..., description="Name of the agent")
    system_message: str = Field("", description="System message")
    default_auto_reply: str | None = Field(None, description="Default auto reply")
    code_execution_config: CodeExecutionConfig = Field(
        CodeExecutionConfig(), description="Configuration for code execution"
    )


class AgentFlowSpec(BaseModel):
    """Config for an agent"""

    id: str | None = Field(None, description="Unique identifier for the configuration")
    type: Literal["assistant", "userproxy", "groupchat"] = Field("userproxy", description="Type of the agent")
    config: AgentConfig = Field(..., description="Agent configuration")
    timestamp: str | None = Field(None, description="Timestamp of the last update")
    skills: list[str] = Field(default_factory=list, description="List of skill names equipped by the agent")
    description: str = Field("", description="Description of the agent")
    user_id: str | None = Field(None, description="The user ID owning this configuration")


class AgentFlowSpecForApi(AgentFlowSpec):
    """Config for an agent, corresponds to IAgentFlowSpec in the frontend"""

    skills: list[str] = Field(default_factory=list, description="List of skill names equipped by the agent")
