import logging
from pathlib import Path

import tiktoken

from nalgonda.repositories.env_config_firestore_storage import EnvConfigFirestoreStorage
from nalgonda.services.oai_client import get_openai_client

logger = logging.getLogger(__name__)


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
    client = get_openai_client(env_config_storage=EnvConfigFirestoreStorage())
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt},
        ],
        **kwargs,
    )
    return completion.choices[0].message.content


def tokenize(text: str) -> list[int]:
    """Tokenize a string using tiktoken tokenizer."""
    return tiktoken.get_encoding("cl100k_base").encode(text)


def get_token_count(text: str) -> int:
    """Get the number of tokens using tiktoken tokenizer."""
    return len(tokenize(text))


def chunk_input_with_token_limit(input_str: str, max_tokens: int, delimiter: str) -> list:
    chunks = []
    parts = input_str.split(delimiter)
    current_chunk: list[str] = []

    current_tokens = 0
    for part in parts:
        part_token_count = get_token_count(part + delimiter)
        if current_tokens + part_token_count > max_tokens:
            new_chunk = delimiter.join(current_chunk)
            if get_token_count(new_chunk) > max_tokens:
                logger.warning(f"Part of the input is longer than {max_tokens} tokens.")
                new_chunk = truncate_oversized_chunk(new_chunk, max_tokens=max_tokens, delimiter=delimiter)
            chunks.append(new_chunk + delimiter)
            current_chunk = [part]
            current_tokens = part_token_count
        else:
            current_chunk.append(part)
            current_tokens += part_token_count

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(delimiter.join(current_chunk) + delimiter)

    return chunks


def truncate_oversized_chunk(chunk: str, max_tokens: int, delimiter: str) -> str:
    """Truncate the chunk if it is longer than max_tokens."""
    tokens = tokenize(chunk + delimiter)
    if len(tokens) > max_tokens:
        tokens = tokens[: max_tokens - get_token_count(delimiter)]
        chunk = tiktoken.get_encoding("gpt-4").decode(tokens)
        chunk += delimiter
    return chunk
