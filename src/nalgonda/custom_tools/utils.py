import tempfile
from pathlib import Path

from agency_swarm.util import get_openai_client


def get_chat_completion(user_prompt, system_message, **kwargs) -> str:
    """
    Generate a chat completion based on a prompt and a system message.
    This function is a wrapper around the OpenAI API.
    """
    from config import settings

    client = get_openai_client()
    completion = client.chat.completions.create(
        model=settings.gpt_model,
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        **kwargs,
    )

    return str(completion.choices[0].message.content)


def check_directory_traversal(dir_path: str) -> Path:
    """
    Ensures that the given directory path is within allowed paths.
    """
    path = Path(dir_path)
    if ".." in path.parts:
        raise ValueError("Directory traversal is not allowed.")

    allowed_bases = [Path(tempfile.gettempdir()).resolve(), Path.home().resolve()]
    if not any(str(path.resolve()).startswith(str(base)) for base in allowed_bases):
        raise ValueError("Directory traversal is not allowed.")
    return path
