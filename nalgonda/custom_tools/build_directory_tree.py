from pathlib import Path

from agency_swarm import BaseTool
from pydantic import Field, field_validator

from nalgonda.custom_tools.utils import check_directory_traversal


class BuildDirectoryTree(BaseTool):
    """Print the structure of directories and files.
    Directory traversal is not allowed (you cannot read /* or ../*).
    """

    start_directory: Path = Field(
        default_factory=Path.cwd,
        description="The starting directory for the tree, defaults to the current working directory.",
    )
    file_extensions: set[str] = Field(
        default_factory=set,
        description="Set of file extensions to include in the tree. If empty, all files will be included. "
        "Examples are {'.py', '.txt', '.md'}.",
    )

    _validate_start_directory = field_validator("start_directory", mode="after")(check_directory_traversal)

    def run(self) -> str:
        """Recursively print the tree of directories and files using pathlib."""
        tree_str = ""
        start_path = self.start_directory.resolve()

        def recurse(directory: Path, level: int = 0) -> None:
            nonlocal tree_str
            indent = " " * 4 * level
            tree_str += f"{indent}{directory.name}\n"
            sub_indent = " " * 4 * (level + 1)

            for path in sorted(directory.iterdir()):
                # ignore hidden files and directories
                if path.is_dir() and not path.name.startswith("."):
                    recurse(path, level + 1)
                elif path.is_file() and (not self.file_extensions or path.suffix in self.file_extensions):
                    tree_str += f"{sub_indent}{path.name}\n"

        recurse(start_path)

        if len(tree_str) > 20000:
            tree_str = tree_str[:20000] + "\n\n... (truncated output, please use a smaller directory or apply a filter)"
        return tree_str


if __name__ == "__main__":
    print(BuildDirectoryTree().run())
