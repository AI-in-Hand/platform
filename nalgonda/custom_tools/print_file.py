from pathlib import Path

from agency_swarm import BaseTool
from pydantic import Field, field_validator

from nalgonda.custom_tools.utils import check_directory_traversal


class PrintFileContents(BaseTool):
    """Print the contents of a specific file."""

    file_name: Path = Field(
        ..., description="The name of the file to be printed. It can be a relative or absolute path."
    )

    _validate_file_name = field_validator("file_name", mode="after")(check_directory_traversal)

    def run(self) -> str:
        """Returns contents of the specified file."""
        file_path = Path(self.file_name).resolve()

        if file_path.is_file():
            return f"{str(file_path)}:\n```\n{self.read_file(file_path)}\n```\n"
        else:
            return f"File {self.file_name} not found or is not a file."

    @staticmethod
    def read_file(file_path: Path):
        """Read and return the contents of a file."""
        try:
            return file_path.read_text()
        except OSError as e:
            return f"Error reading file {file_path}: {e}"


if __name__ == "__main__":
    print(
        PrintFileContents(
            file_name="example.txt",
        ).run()
    )
