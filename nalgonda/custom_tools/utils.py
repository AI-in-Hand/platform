from pathlib import Path

from agency_swarm.util import get_openai_client


def get_chat_completion(user_prompt: str, system_message: str, model: str, **kwargs) -> str:
    """Generate a chat completion based on a prompt and a system message.
    This function is a wrapper around the OpenAI API."""
    client = get_openai_client()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt},
        ],
        **kwargs,
    )
    return completion.choices[0].message.content


def check_directory_traversal(path: Path) -> Path:
    """Ensures that the given path (file or directory) is within allowed paths."""
    if ".." in path.parts:
        raise ValueError("Directory traversal is not allowed.")

    base_directory = Path.cwd()

    # Resolve the path against the base directory
    resolved_path = (base_directory / path).resolve()

    # Check if the resolved path is a subpath of the base directory
    if not resolved_path.is_relative_to(base_directory):
        raise ValueError("Directory traversal is not allowed.")

    return resolved_path
