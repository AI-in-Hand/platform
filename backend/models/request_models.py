from pydantic import BaseModel, Field


class SkillExecutePostRequest(BaseModel):
    id: str = Field(..., description="The unique identifier for the skill.")
    user_prompt: str = Field(..., description="The user prompt to extract parameters from.")
