from pathlib import Path

from agency_swarm import BaseTool
from pydantic import Field, field_validator

from nalgonda.custom_tools.utils import check_directory_traversal


class PrintAllFilesInPath(BaseTool):
    """Print the contents of all files in a start_path recursively.
    The parameters are: start_path, file_extensions.
    Directory traversal is not allowed (you cannot read /* or ../*).
    """

    start_path: Path = Field(
        default_factory=Path.cwd,
        description="Directory to search for files, by default the current working directory.",
    )
    file_extensions: set[str] = Field(
        default_factory=set,
        description="Set of file extensions to include in the tree. If empty, all files will be included. "
        "Examples are {'.py', '.txt', '.md'}.",
    )

    _validate_start_path = field_validator("start_path", mode="after")(check_directory_traversal)

    def run(self) -> str:
        """
        Recursively searches for files within `start_path` and compiles their contents into a single string.
        """
        output = []
        start_path = self.start_path.resolve()

        for path in start_path.rglob("*"):
            # ignore files in hidden directories
            if any(part.startswith(".") for part in path.parts):
                continue
            if path.is_file() and (not self.file_extensions or path.suffix in self.file_extensions):
                output.append(f"{str(path)}:\n```\n{self.read_file(path)}\n```\n")

        output_str = "\n".join(output)

        if len(output_str) > 20000:
            output_str = (
                output_str[:20000] + "\n\n... (truncated output, please use a smaller directory or apply a filter)"
            )
        return output_str

    @staticmethod
    def read_file(file_path: Path):
        """Read and return the contents of a file."""
        try:
            return file_path.read_text()
        except OSError as e:
            return f"Error reading file {file_path}: {e}"


if __name__ == "__main__":
    print(
        PrintAllFilesInPath(
            start_path=".",
            file_extensions={".py", ".json", ".yaml", ".yml", ".md", ".txt", ".tsx", ".ts", ".js", ".jsx", ".html"},
        ).run()
    )
