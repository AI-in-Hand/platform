import os

from agency_swarm import BaseTool
from pydantic import Field


class PrintAllFilesInDirectory(BaseTool):
    """Print the contents of all files in a start_directory recursively."""

    start_directory: str = Field(
        default_factory=lambda: os.getcwd(),
        description="Directory to search for Python files, by default the current working directory.",
    )
    file_extensions: list[str] | None = Field(
        default_factory=lambda: None,
        description="List of file extensions to include in the output. If None, all files will be included.",
    )

    def run(self) -> str:
        """Run the tool."""
        self._validate_start_directory()

        output = []
        for root, _, files in os.walk(self.start_directory, topdown=True):
            for file in files:
                if self.file_extensions is None or file.endswith(tuple(self.file_extensions)):
                    file_path = os.path.join(root, file)
                    output.append(f"{file_path}:\n```\n{self.read_file(file_path)}\n```\n")
        return "\n".join(output)

    @staticmethod
    def read_file(file_path):
        try:
            with open(file_path, "r") as file:
                return file.read()
        except IOError as e:
            return f"Error reading file {file_path}: {e}"

    def _validate_start_directory(self):
        """Do not allow directory traversal."""
        if ".." in self.start_directory or (
            self.start_directory.startswith("/") and not self.start_directory.startswith("/tmp")
        ):
            raise ValueError("Directory traversal is not allowed.")
