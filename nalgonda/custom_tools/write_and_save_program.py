from pathlib import Path

from agency_swarm import BaseTool
from pydantic import Field

from nalgonda.constants import AGENCY_DATA_DIR


class File(BaseTool):
    """
    File to be written to the disk with an appropriate name and file path,
    containing code that can be saved and executed locally at a later time.
    """

    file_name: str = Field(
        ...,
        description="The name of the file including the extension and the file path from your current directory "
        "if needed.",
    )
    chain_of_thought: str = Field(
        ..., description="Think step by step to determine the correct plan that is needed to write the file."
    )
    body: str = Field(..., description="Correct contents of a file")

    def run(self):
        if ".." in self.file_name or self.file_name.startswith("/"):
            return "Invalid file path. Directory traversal is not allowed."

        # Extract the directory path from the file name
        directory_path = Path(self.file_name).parent
        agency_id = "test_agency_id"  # agency_id = self.context["agency_id"]  # TODO: pass agency_id to all tools
        directory = AGENCY_DATA_DIR / agency_id / directory_path

        # Ensure the directory exists
        directory.mkdir(parents=True, exist_ok=True)

        # Construct the full path using the directory and file name
        full_path = directory / Path(self.file_name).name

        # Write the file
        with open(full_path, "w") as f:
            f.write(self.body)

        return "File written to " + full_path.as_posix()


class WriteAndSaveProgram(BaseTool):
    """Set of files that represent a complete and correct program/application"""

    chain_of_thought: str = Field(
        ..., description="Think step by step to determine the correct actions that are needed to implement the program."
    )
    files: list[File] = Field(..., description="List of files")

    def run(self):
        outputs = []
        for file in self.files:
            outputs.append(file.run())

        return str(outputs)
