from pathlib import Path

from agency_swarm import get_openai_client


def init_webserver_folders(root_file_path: Path) -> dict[str, Path]:
    """
    Initialize folders needed for a web server, such as static file directories
    and user-specific data directories.

    :param root_file_path: The root directory where webserver folders will be created
    :return: A dictionary with the path of each created folder
    """
    static_folder_root = root_file_path / "ui"
    static_folder_root.mkdir(parents=True, exist_ok=True)
    folders = {
        "static_folder_root": static_folder_root,
    }
    return folders


def get_chat_completion(system_message: str, user_prompt: str, model: str, **kwargs) -> str:
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
