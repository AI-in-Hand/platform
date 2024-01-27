from nalgonda.settings import settings
from nalgonda.utils import get_chat_completion

TOOL_SUMMARY_SYSTEM_MESSAGE = """\
As a supportive assistant, ensure your responses are concise,
confined to a single sentence, and rigorously comply with the specified instructions.\
"""
USER_PROMPT = "In one succinct sentence, describe the functionality of the tool provided below:\n"


def generate_tool_description(code: str):
    summary = get_chat_completion(
        system_message=TOOL_SUMMARY_SYSTEM_MESSAGE,
        user_prompt=f"{USER_PROMPT}```\n{code}\n```",
        temperature=0.0,
        model=settings.gpt_cheap_model,
    )
    return summary
