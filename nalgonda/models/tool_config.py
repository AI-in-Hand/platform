from pydantic import BaseModel, Field


class ToolConfig(BaseModel):
    """Tool configuration model"""

    tool_id: str | None = Field(None, description="The unique ID of the tool configuration")
    owner_id: str | None = Field(None, description="The user ID owning this tool configuration")
    name: str = Field(..., description="Name of the tool")
    version: int = Field(1, description="Version of the tool configuration")
    code: str = Field(..., description="The actual code of the tool")
    approved: bool = Field(False, description="Approval status of the tool configuration")

    def increment_version(self):
        """Increment the tool's version."""
        self.version += 1
