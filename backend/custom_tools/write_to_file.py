from agency_swarm.tools import BaseTool
from pydantic import Field


class MyCustomTool(BaseTool):
    """
    A brief description of what the custom tool does.
    The docstring should clearly explain the tool's purpose and functionality.
    """

    example_field: str = Field(..., description="Description of the example field, explaining its purpose and usage.")

    def run(self):
        return "Result of MyCustomTool operation"
