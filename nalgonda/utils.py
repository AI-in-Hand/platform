from pathlib import Path


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
