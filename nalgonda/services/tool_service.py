import json
import logging

from agency_swarm import BaseTool

from nalgonda import custom_tools
from nalgonda.settings import settings
from nalgonda.utils import get_chat_completion

TOOL_SUMMARY_SYSTEM_MESSAGE = """\
As a supportive assistant, ensure your responses are concise,
confined to a single sentence, and rigorously comply with the specified instructions.\
"""
USER_PROMPT = "In one succinct sentence, describe the functionality of the tool provided below:\n"

logger = logging.getLogger(__name__)


def generate_tool_description(code: str):
    summary = get_chat_completion(
        system_message=TOOL_SUMMARY_SYSTEM_MESSAGE,
        user_prompt=f"{USER_PROMPT}```\n{code}\n```",
        temperature=0.0,
        model=settings.gpt_cheap_model,
    )
    return summary


class ToolService:
    SYSTEM_MESSAGE = """\
You are an assistant that responds with JSON only. You are presented with a user prompt and a function specification, \
and you MUST return the function call parameters in JSON format.
For example, if the function has parameters file_name and file_size, \
and the user prompt is ```file name is test.txt, and the size is 1MB```, \
then the function call parameters are {\"file_name\": \"test.txt\", \"file_size\": \"1MB\"}
The function call parameters must be returned in JSON format.\
"""
    USER_PROMPT_PREFIX = "Return the function call parameters in JSON format based on the following user prompt: "

    def execute_tool(self, tool_name: str, user_prompt: str):
        """
        Import the tool from nalgonda.custom_tools package, initialize it (using GPT to fill in kwargs), and run it
        """
        tool_class = self._get_tool_class(tool_name)
        tool_args = self._get_tool_arguments(json.dumps(tool_class.openai_schema), user_prompt)
        return self._execute_tool(tool_class, tool_args)

    def _get_tool_class(self, tool_name: str) -> BaseTool:
        """Get a tool function by name from nalgonda.custom_tools"""
        try:
            return getattr(custom_tools, tool_name)
        except AttributeError as e:
            logger.exception(f"Tool {tool_name} not found")
            raise Exception(f"Tool {tool_name} not found") from e

    def _get_tool_arguments(self, function_spec: str, user_prompt: str) -> str:
        user_prompt = (
            f"{self.USER_PROMPT_PREFIX}\n```\n{user_prompt}\n```. \n"
            f"The function specification:\n```{function_spec}```"
        )
        args_str = get_chat_completion(
            system_message=self.SYSTEM_MESSAGE, user_prompt=user_prompt, temperature=0.0, model=settings.gpt_model
        )
        return args_str.strip("`json\n ").replace("\n", "")

    def _execute_tool(self, tool_class: BaseTool, args: str):
        if not tool_class:
            return f"Error: Tool {tool_class.__name__} not found"

        try:
            # init tool
            func = tool_class(**eval(args))
            # get outputs from the tool
            return func.run()
        except Exception as e:
            error_message = f"Error: {e}"
            if "For further information visit" in error_message:
                error_message = error_message.split("For further information visit")[0]
            return error_message
