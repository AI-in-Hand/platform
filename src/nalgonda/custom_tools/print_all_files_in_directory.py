from pathlib import Path

from agency_swarm import BaseTool
from pydantic import Field, field_validator

from nalgonda.custom_tools.utils import check_directory_traversal


class PrintAllFilesInDirectory(BaseTool):
    """Print the contents of all files in a start_directory recursively.
    Directory traversal is not allowed (you cannot read /* or ../*).
    """

    start_directory: Path = Field(
        default_factory=Path.cwd,
        description="Directory to search for Python files, by default the current working directory.",
    )
    file_extensions: set[str] = Field(
        default_factory=set,
        description="Set of file extensions to include in the output. If empty, all files will be included.",
    )

    _validate_start_directory = field_validator("start_directory", mode="before")(check_directory_traversal)

    def run(self) -> str:
        """
        Recursively searches for files within `start_directory` and compiles their contents into a single string.
        """
        output = []
        start_path = self.start_directory.resolve()

        for path in start_path.rglob("*"):
            if path.is_file() and (not self.file_extensions or path.suffix in self.file_extensions):
                output.append(f"{str(path)}:\n```\n{self.read_file(path)}\n```\n")

        return "\n".join(output)

    @staticmethod
    def read_file(file_path: Path):
        """Read and return the contents of a file."""
        try:
            return file_path.read_text()
        except OSError as e:
            return f"Error reading file {file_path}: {e}"
