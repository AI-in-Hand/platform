import os

from custom_tools import PrintAllFilesInDirectory


def test_print_all_files_no_extension_filter(temp_dir):
    """
    Test if PrintAllFilesInDirectory correctly prints contents of all files when no file extension filter is applied.
    """
    pafid = PrintAllFilesInDirectory(directory=str(temp_dir))
    expected_output = (
        f"{os.path.join(temp_dir, 'sub', 'test.py')}:\n```\nprint('hello')\n```\n\n"
        f"{os.path.join(temp_dir, 'sub', 'test.txt')}:\n```\nhello world\n```\n"
    )
    assert pafid.run() == expected_output


def test_print_all_files_with_py_extension(temp_dir):
    """
    Test if PrintAllFilesInDirectory correctly prints contents of .py files only.
    """
    pafid = PrintAllFilesInDirectory(directory=str(temp_dir), file_extensions=[".py"])
    expected_output = f"{os.path.join(temp_dir, 'sub', 'test.py')}:\n```\nprint('hello')\n```\n"
    assert pafid.run() == expected_output


def test_print_all_files_with_txt_extension(temp_dir):
    """
    Test if PrintAllFilesInDirectory correctly prints contents of .txt files only.
    """
    pafid = PrintAllFilesInDirectory(directory=str(temp_dir), file_extensions=[".txt"])
    expected_output = f"{os.path.join(temp_dir, 'sub', 'test.txt')}:\n```\nhello world\n```\n"
    assert pafid.run() == expected_output


def test_print_all_files_error_reading_file(temp_dir):
    """
    Test if PrintAllFilesInDirectory handles errors while reading a file.
    """
    # Create an unreadable file
    unreadable_file = os.path.join(temp_dir, "unreadable_file.txt")
    with open(unreadable_file, "w") as f:
        f.write("content")
    os.chmod(unreadable_file, 0o000)  # make the file unreadable

    pafid = PrintAllFilesInDirectory(directory=str(temp_dir), file_extensions=[".txt"])
    assert "Error reading file" in pafid.run()

    os.chmod(unreadable_file, 0o644)  # reset file permissions for cleanup
