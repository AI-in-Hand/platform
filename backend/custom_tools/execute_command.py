import shlex
import subprocess

from agency_swarm import BaseTool
from pydantic import Field

allowed_commands = [
    "git",
    "pip",
    "poetry",
    "pytest",
    "pre-commit",
    "mypy",
    "ruff",
    "flake8",
    "black",
    "isort",
    "sqlite3",
]


class ExecuteCommand(BaseTool):
    """
    Run specific allowed commands from the terminal. This is restricted to a predefined set of
    developer tools commands for tasks such as package management, testing, linting, and formatting.
    Allowed commands include:
    'git', 'pip', 'poetry', 'pytest', 'pre-commit', 'mypy', 'ruff', 'flake8', 'black', 'isort', 'sqlite3'

    If there are too many logs, the outputs might be truncated.

    The command should be one of the allowed commands followed by its arguments. For example:
    'pip install flask' or 'pytest tests/'. 'poetry run *' is generally not allowed, except for
    'poetry run pytest'.
    """

    command: str = Field(
        ..., description="The command to be executed, restricted to a specific set of allowed commands."
    )

    def run(self):
        """Executes the given command and captures its output and errors."""
        command_args = shlex.split(self.command)

        # Validate the command
        if command_args[0] not in allowed_commands:
            return f"Command '{command_args[0]}' is not allowed."

        # Special handling for 'poetry run'
        if command_args[0] == "poetry" and command_args[1] == "run" and command_args[2] != "pytest":
            return "Only 'poetry run pytest' is allowed."

        try:
            result = subprocess.run(command_args, shell=False, text=True, capture_output=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"An error occurred: {e.stderr}"
