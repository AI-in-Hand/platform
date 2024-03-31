from typing import Any

from pydantic import BaseModel, Field

from backend.models.agent_flow_spec import AgentFlowSpecForApi
from backend.models.skill_config import SkillConfig


class BaseResponse(BaseModel):
    status: bool = Field(True, description="The status of the response.")
    message: str = Field("", description="The message to be displayed.")


# =================================================================================================
# Skills API


class GetSkillListResponse(BaseResponse):
    data: list[SkillConfig] = Field(..., description="The list of skill configurations.")


class GetSkillResponse(BaseResponse):
    data: SkillConfig = Field(..., description="The skill configuration.")


class CreateSkillVersionData(BaseModel):
    id: str = Field(..., description="The unique identifier of the skill.")
    version: int = Field(..., description="The version of the skill.")


class CreateSkillVersionResponse(BaseResponse):
    data: CreateSkillVersionData = Field(..., description="The data to be returned.")


class ExecuteSkillResponse(BaseResponse):
    data: Any = Field(..., description="The data to be returned.")


# =================================================================================================
# Agents API


class GetAgentListResponse(BaseResponse):
    data: list[AgentFlowSpecForApi] = Field(..., description="The list of agent configurations.")


class GetAgentResponse(BaseResponse):
    data: AgentFlowSpecForApi = Field(..., description="The agent configuration.")


class CreateAgentData(BaseModel):
    id: str = Field(..., description="The unique identifier of the agent.")


class CreateAgentResponse(BaseResponse):
    data: CreateAgentData = Field(..., description="The data to be returned.")


# =================================================================================================
# Version API


class VersionData(BaseModel):
    version: str = Field(..., description="The version of the API.")


class VersionResponse(BaseResponse):
    data: VersionData = Field(..., description="The data to be returned.")
