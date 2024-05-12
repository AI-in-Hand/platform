from agency_swarm import BaseTool
from pydantic import Field

from backend.repositories.s3_storage import S3Handler
from backend.repositories.user_variable_storage import UserVariableStorage
from backend.services.user_variable_manager import UserVariableManager


class File(BaseTool):
    """File to be written to the disk with an appropriate name and file path,
    containing code that can be saved and executed locally at a later time.
    """

    file_name: str = Field(
        ...,
        description="The name of the file including the extension and the file path from your current directory.",
    )
    chain_of_thought: str = Field(
        ...,
        description="Think step by step to determine the correct plan that is needed to write the file.",
    )
    body: str = Field(..., description="Correct contents of a file")

    def run(self) -> str:
        user_variable_manager = UserVariableManager(UserVariableStorage())
        aws_access_key_id = user_variable_manager.get_by_key("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = user_variable_manager.get_by_key("AWS_SECRET_ACCESS_KEY")
        bucket_name = user_variable_manager.get_by_key("AWS_BUCKET_NAME")

        s3_handler = S3Handler(aws_access_key_id, aws_secret_access_key, bucket_name)
        return s3_handler.upload_file(self.file_name, self.body)


class WriteAndSaveProgram(BaseTool):
    """Set of files that represent a complete and correct program/application"""

    chain_of_thought: str = Field(
        ...,
        description="Think step by step to determine the correct actions that are needed to implement the program.",
    )
    files: list[File] = Field(..., description="List of files")

    def run(self) -> str:
        outputs = [file.run() for file in self.files]
        return str(outputs)
