from typing import Any

from pydantic import BaseModel, Field

from backend.models.skill_config import SkillConfig


class BaseResponse(BaseModel):
    status: bool = Field(True, description="The status of the response.")
    message: str = Field("", description="The message to be displayed.")


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


class VersionData(BaseModel):
    version: str = Field(..., description="The version of the API.")


class VersionResponse(BaseResponse):
    data: VersionData = Field(..., description="The data to be returned.")
