from pathlib import Path

from agency_swarm.util import get_openai_client

from nalgonda.settings import settings


def get_chat_completion(user_prompt: str, system_message: str, **kwargs) -> str:
    """Generate a chat completion based on a prompt and a system message.
    This function is a wrapper around the OpenAI API."""
    client = get_openai_client()
    completion = client.chat.completions.create(
        model=settings.gpt_model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt},
        ],
        **kwargs,
    )
    return completion.choices[0].message.content


def check_directory_traversal(directory: Path) -> Path:
    """Ensures that the given directory path is within allowed paths."""
    if ".." in directory.parts:
        raise ValueError("Directory traversal is not allowed.")

    base_directory = Path.cwd()

    # Resolve the directory path against the base directory
    resolved_directory = (base_directory / directory).resolve()

    # Check if the resolved directory is a subpath of the base directory
    if not resolved_directory.is_relative_to(base_directory):
        raise ValueError("Directory traversal is not allowed.")

    return resolved_directory
