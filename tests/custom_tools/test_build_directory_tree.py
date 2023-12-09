import os

from nalgonda.custom_tools import BuildDirectoryTree


def test_build_directory_tree_with_py_extension(temp_dir):
    """
    Test if BuildDirectoryTree correctly lists only .py files in the directory tree.
    """
    bdt = BuildDirectoryTree(start_directory=str(temp_dir), file_extensions=[".py"])
    expected_output = f"{temp_dir.name}\n    sub\n        test.py\n"
    assert bdt.run() == expected_output


def test_build_directory_tree_with_multiple_extensions(temp_dir):
    """
    Test if BuildDirectoryTree lists files with multiple specified extensions.
    """
    bdt = BuildDirectoryTree(start_directory=str(temp_dir), file_extensions=[".py", ".txt"])
    expected_output = {
        f"{temp_dir.name}",
        "    sub",
        "        test.py",
        "        test.txt",
    }
    actual_output = set(bdt.run().strip().split("\n"))
    assert actual_output == expected_output


def test_build_directory_tree_default_settings():
    """
    Test if BuildDirectoryTree uses the correct default settings.
    """
    bdt = BuildDirectoryTree()
    assert bdt.start_directory == os.getcwd()
    assert bdt.file_extensions is None
