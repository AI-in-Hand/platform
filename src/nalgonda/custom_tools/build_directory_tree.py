import os

from agency_swarm import BaseTool
from pydantic import Field


class BuildDirectoryTree(BaseTool):
    """Print the structure of directories and files."""

    start_directory: str = Field(
        default_factory=lambda: os.getcwd(),
        description="The starting directory for the tree, defaults to the current working directory.",
    )
    file_extensions: list[str] | None = Field(
        default_factory=lambda: None,
        description="List of file extensions to include in the tree. If None, all files will be included.",
    )

    def run(self) -> str:
        """Run the tool."""
        self._validate_start_directory()
        tree_str = self.print_tree()
        return tree_str

    def print_tree(self):
        """Recursively print the tree of directories and files using os.walk."""
        tree_str = ""

        for root, _, files in os.walk(self.start_directory, topdown=True):
            level = root.replace(self.start_directory, "").count(os.sep)
            indent = " " * 4 * level
            tree_str += f"{indent}{os.path.basename(root)}\n"
            sub_indent = " " * 4 * (level + 1)

            for f in files:
                if not self.file_extensions or f.endswith(tuple(self.file_extensions)):
                    tree_str += f"{sub_indent}{f}\n"

        return tree_str

    def _validate_start_directory(self):
        """Do not allow directory traversal."""
        if ".." in self.start_directory or (
            self.start_directory.startswith("/") and not self.start_directory.startswith("/tmp")
        ):
            raise ValueError("Directory traversal is not allowed.")
