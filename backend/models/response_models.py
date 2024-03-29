from pydantic import BaseModel, Field

from backend.models.skill_config import SkillConfig


class BaseResponse(BaseModel):
    status: bool = Field(True, description="The status of the response.")
    message: str = Field("", description="The message to be displayed.")
    data: BaseModel = Field(..., description="The data to be returned.")


class GetSkillListResponse(BaseResponse):
    data: list[SkillConfig] = Field(..., description="The list of skill configurations.")


class CreateSkillVersionData(BaseModel):
    id: str = Field(..., description="The unique identifier of the skill.")
    version: str = Field(..., description="The version of the skill.")


class CreateSkillVersionResponse(BaseResponse):
    data: CreateSkillVersionData = Field(..., description="The data to be returned.")


class VersionData(BaseModel):
    version: str = Field(..., description="The version of the API.")


class VersionResponse(BaseResponse):
    data: VersionData = Field(..., description="The data to be returned.")
