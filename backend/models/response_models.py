from typing import Any

from pydantic import BaseModel, Field

from backend.models.agency_config import AgencyConfigForAPI
from backend.models.agent_flow_spec import AgentFlowSpecForAPI
from backend.models.message import Message
from backend.models.session_config import SessionConfigForAPI
from backend.models.skill_config import SkillConfig


class BaseResponse(BaseModel):
    status: bool = Field(True, description="The status of the response.")
    message: str = Field("Success", description="The message to be displayed.")


# =================================================================================================
# Skills API


class SkillListResponse(BaseResponse):
    data: list[SkillConfig] = Field(..., description="The list of skill configurations.")


class GetSkillResponse(BaseResponse):
    data: SkillConfig = Field(..., description="The skill configuration.")


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


class CreateSessionResponse(BaseResponse):
    data: list[SessionConfigForAPI] = Field(..., description="The list of session configurations.")
    session_id: str = Field(..., description="The unique identifier of the session.")


# =================================================================================================
# Message API


class MessagePostResponse(BaseResponse):
    data: list[Message] = Field(..., description="The list of messages.")
    response: str = Field(..., description="The final agent response.")


# =================================================================================================
# User API


class UserVariablesResponse(BaseResponse):
    data: list[str] = Field(..., description="The list of variable names.")


# =================================================================================================
# Version API


class VersionData(BaseModel):
    version: str = Field(..., description="The version of the API.")


class VersionResponse(BaseResponse):
    data: VersionData = Field(..., description="The data to be returned.")


# =================================================================================================
# User Profile API Response

class UserProfileResponse(BaseResponse):
    data: dict[str, str] = Field(..., description="User profile data.")
