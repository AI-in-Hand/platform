from pathlib import Path


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
