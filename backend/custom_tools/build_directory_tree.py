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
        tree_str = self.print_tree(self.start_directory, "")
        return tree_str

    def print_tree(self, directory, indent):
        # Print the name of the directory
        tree_str = f"{indent}{os.path.basename(directory)}\n"
        indent += "    "

        # Loop through the contents of the directory
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            # Check if the item is a directory
            if os.path.isdir(path):
                tree_str += self.print_tree(path, indent)
            else:
                # If it's a file, just print its name
                if self.file_extensions is None or path.endswith(tuple(self.file_extensions)):
                    tree_str += f"{indent}{os.path.basename(path)}\n"

        return tree_str
