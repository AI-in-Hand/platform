import inspect
import os

from agency_swarm import BaseTool
from fastapi import WebSocket
from pydantic import Field

from constants import DATA_DIR


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
    body: str = Field(..., description="Correct contents of a file")

    def run(self):
        # Extract the directory path from the file name
        directory = DATA_DIR / self._session_id / os.path.dirname(self.file_name)
        full_path = directory / self.file_name

        # If the directory is not empty, check if it exists and create it if not
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Write the file
        with open(full_path, "w") as f:
            f.write(self.body)

        return "File written to " + full_path

    @property
    def _session_id(self):
        """Using inspect, get the session_id from the WebSocket connection."""

        # Searching for the first WebSocket instance in the call stack
        for frame_record in inspect.stack():
            websocket_instance = next(
                (v for v in frame_record.frame.f_locals.values() if isinstance(v, WebSocket)), None
            )
            if websocket_instance:
                # Extracting session ID from path_params
                return websocket_instance.path_params.get("session_id")
        return None


class WriteAndSaveProgram(BaseTool):
    """Set of files that represent a complete and correct program.
    This environment has access to all standard Python packages and the internet."""

    chain_of_thought: str = Field(
        ..., description="Think step by step to determine the correct actions that are needed to implement the program."
    )
    files: list[File] = Field(..., description="List of files")

    def run(self):
        outputs = []
        for file in self.files:
            outputs.append(file.run())

        return str(outputs)
