import shlex
import subprocess

from agency_swarm import BaseTool
from pydantic import Field


class ExecuteCommand(BaseTool):
    """Run any command from the terminal. If there are too many logs, the outputs might be truncated.

    Note: When using package management tools like pip or poetry, ensure they operate within
    the context of the newly created virtual environment. Avoid global installations or modifications.

    The way the command is executed is:
    `subprocess.run(command, cwd=cwd, shell=False, text=True, capture_output=True, check=True)`
    """

    command: str = Field(..., description="The command to be executed.")
    cwd: str = Field(
        default=".",
        description="The directory from which the command should be executed. "
        "By default, the current working directory is used.",
    )

    def run(self):
        """Executes the given command and captures its output and errors."""
        try:
            # Splitting the command into a list of arguments
            command_args = shlex.split(self.command)

            # Executing the command
            result = subprocess.run(command_args, cwd=self.cwd, shell=False, text=True, capture_output=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"An error occurred: {e.stderr}"
