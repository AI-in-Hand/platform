from pathlib import Path

import pytest

from nalgonda.custom_tools import PrintFileContents


@pytest.fixture
def create_file_in_path(tmp_path: Path) -> Path:
    # Create a file and write contents to it
    file_path = tmp_path / "example.txt"
    file_path.write_text("File content")
    return file_path


def test_print_file_contents(create_file_in_path: Path):
    tool = PrintFileContents(file_name=str(create_file_in_path))
    result = tool.run()
    expected_result = f"{str(create_file_in_path)}:\n```\nFile content\n```\n"
    assert result == expected_result


def test_print_file_contents_error(create_file_in_path):
    # Create a scenario for a file that doesn't exist
    non_existent_file = create_file_in_path.parent / "non_existent.txt"
    tool = PrintFileContents(file_name=str(non_existent_file))
    result = tool.run()
    assert "non_existent.txt not found or is not a file." in result
