from pydantic import BaseModel, Field


class SkillConfig(BaseModel):
    """Skill configuration model"""

    id: str | None = Field(None, description="Unique identifier for the configuration")
    owner_id: str | None = Field(None, description="The user ID owning this configuration")
    title: str = Field(..., description="Name of the skill")
    description: str = Field("", description="Description of the skill")
    version: int = Field(1, description="Version of the skill configuration")
    content: str = Field("", description="The actual code of the skill")
    approved: bool | None = Field(None, description="Approval status of the skill configuration")

    def increment_version(self):
        """Increment the skill's version."""
        self.version += 1