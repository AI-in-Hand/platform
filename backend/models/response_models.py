from typing import Any

from pydantic import BaseModel, Field

from backend.models.agency_config import AgencyConfigForAPI
from backend.models.agent_flow_spec import AgentFlowSpecForAPI
from backend.models.session_config import SessionConfigForAPI
from backend.models.skill_config import SkillConfig


class BaseResponse(BaseModel):
    status: bool = Field(True, description="The status of the response.")
    message: str = Field("Success", description="The message to be displayed.")


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


class AgentListResponse(BaseResponse):
    data: list[AgentFlowSpecForAPI] = Field(..., description="The list of agent configurations.")


class GetAgentResponse(BaseResponse):
    data: AgentFlowSpecForAPI = Field(..., description="The agent configuration.")


# =================================================================================================
# Agency API


class AgencyListResponse(BaseResponse):
    data: list[AgencyConfigForAPI] = Field(..., description="The list of agency configurations.")


class GetAgencyResponse(BaseResponse):
    data: AgencyConfigForAPI = Field(..., description="The agency configuration.")


# =================================================================================================
# Session API


class SessionListResponse(BaseResponse):
    data: list[SessionConfigForAPI] = Field(..., description="The list of session configurations.")


# =================================================================================================
# Message API


class MessagePostData(BaseModel):
    content: str = Field(..., description="The content of the message.")


class MessagePostResponse(BaseResponse):
    data: MessagePostData = Field(..., description="The data to be returned.")


# =================================================================================================
# User API


class UserSecretsResponse(BaseResponse):
    data: list[str] = Field(..., description="The list of secret names.")


# =================================================================================================
# Version API


class VersionData(BaseModel):
    version: str = Field(..., description="The version of the API.")


class VersionResponse(BaseResponse):
    data: VersionData = Field(..., description="The data to be returned.")
