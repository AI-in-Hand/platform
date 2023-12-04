import subprocess

from agency_swarm import BaseTool
from pydantic import Field


class ExecuteCommand(BaseTool):
    """Run any command from the terminal. If there are too many logs, the outputs might be truncated."""

    command: str = Field(..., description="The command to be executed.")

    def run(self):
        """Executes the given command and captures its output and errors."""
        try:
            # Splitting the command into a list of arguments
            command_args = self.command.split()

            # Executing the command
            result = subprocess.run(command_args, text=True, capture_output=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"An error occurred: {e.stderr}"
