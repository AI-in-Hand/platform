from pathlib import Path

from agency_swarm import BaseTool
from pydantic import Field

from nalgonda.custom_tools import PrintAllFilesInPath
from nalgonda.settings import settings
from nalgonda.utils import chunk_input_with_token_limit, get_chat_completion

USER_PROMPT_PREFIX = "Summarize the code of each file below.\n\n"
SYSTEM_MESSAGE = """\
Your main job is to handle programming code from SEVERAL FILES. \
Each file's content is shown within triple backticks and has a FILE PATH as a title. \
It's vital to KEEP the FILE PATHS.
Here's what to do:
1. ALWAYS KEEP the FILE PATHS for each file.
2. Start each file with a short SUMMARY of its content. Mention important points but don't repeat details found later.
3. KEEP important elements like non-trivial imports, function details, type hints, and key constants. \
Don't change these.
4. In functions or class methods, replace long code with a short SUMMARY in the docstrings, keeping the main logic.
5. Shorten and combine docstrings and comments into the function or method descriptions.
6. For classes, provide a brief SUMMARY in the docstrings, explaining the class's purpose and main logic.
7. Cut down long strings to keep things brief.
8. If there's a comment about "truncated output" at the end, KEEP it.

Your task is to create a concise version of the code, strictly keeping the FILE PATHS and structure, \
without extra comments or explanations. Focus on clarity and avoiding repeated information within each file.\
"""


class SummarizeAllCodeInPath(BaseTool):
    """Summarize code using GPT-3. The tool uses the `PrintAllFilesInPath` tool to get the code to summarize.
    The parameters are: start_path, file_extensions.
    Directory traversal is not allowed (you cannot read /* or ../*).
    """

    start_path: Path = Field(
        default_factory=Path.cwd,
        description="The starting path to search for files, defaults to the current working directory. "
        "Can be a filename or a directory.",
    )
    file_extensions: set[str] = Field(
        default_factory=set,
        description="Set of file extensions to include in the tree. If empty, all files will be included. "
        "Examples are {'.py', '.txt', '.md'}.",
    )
    truncate_to: int = Field(
        default=None,
        description="Truncate the output to this many characters. If None or skipped, the output is not truncated.",
    )

    def run(self) -> str:
        """Run the tool and return the output."""
        delimiter = "\n```\n"

        full_code = PrintAllFilesInPath(
            start_path=self.start_path,
            file_extensions=self.file_extensions,
        ).run()
        user_prompt = f"{USER_PROMPT_PREFIX}{full_code}"

        # Chunk the input based on token limit
        chunks = chunk_input_with_token_limit(user_prompt, max_tokens=16385, delimiter=delimiter)

        outputs = []
        for chunk in chunks:
            output = get_chat_completion(
                user_prompt=chunk, system_message=SYSTEM_MESSAGE, temperature=0.0, model=settings.gpt_cheap_model
            )
            outputs.append(output)

        # Concatenate and possibly truncate outputs
        concatenated_output = delimiter.join(outputs)
        if self.truncate_to and len(concatenated_output) > self.truncate_to:
            concatenated_output = (
                concatenated_output[: self.truncate_to]
                + "\n\n... (truncated output, please use a smaller directory or apply a filter)"
            )

        return concatenated_output


if __name__ == "__main__":
    print(
        SummarizeAllCodeInPath(
            start_path=".",
            file_extensions={".py"},
        ).run()
    )
