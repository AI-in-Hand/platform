from nalgonda.custom_tools import PrintAllFilesInPath


def test_print_all_files_no_extension_filter(temp_dir):
    """
    Test if PrintAllFilesInPath correctly prints contents of all files when no file extension filter is applied.
    """
    pafid = PrintAllFilesInPath(start_path=temp_dir)
    expected_output = {
        f"{temp_dir}/sub/test.py:\n```\nprint('hello')\n```",
        f"{temp_dir}/sub/test.txt:\n```\nhello world\n```",
    }
    actual_output = set(pafid.run().strip().split("\n\n"))
    assert actual_output == expected_output


def test_print_all_files_with_py_extension(temp_dir):
    """
    Test if PrintAllFilesInPath correctly prints contents of .py files only.
    """
    pafid = PrintAllFilesInPath(start_path=temp_dir, file_extensions={".py"})
    expected_output = f"{temp_dir.joinpath('sub', 'test.py')}:\n```\nprint('hello')\n```\n"
    assert pafid.run() == expected_output


def test_print_all_files_with_txt_extension(temp_dir):
    """
    Test if PrintAllFilesInPath correctly prints contents of .txt files only.
    """
    pafid = PrintAllFilesInPath(start_path=temp_dir, file_extensions={".txt"})
    expected_output = f"{temp_dir.joinpath('sub', 'test.txt')}:\n```\nhello world\n```\n"
    assert pafid.run() == expected_output


def test_print_all_files_error_reading_file(temp_dir):
    """
    Test if PrintAllFilesInPath handles errors while reading a file.
    """
    # Create an unreadable file
    unreadable_file = temp_dir.joinpath("unreadable_file.txt")
    unreadable_file.write_text("content")
    unreadable_file.chmod(0o000)  # make the file unreadable

    pafid = PrintAllFilesInPath(start_path=temp_dir, file_extensions={".txt"})
    assert "Error reading file" in pafid.run()

    unreadable_file.chmod(0o644)  # reset file permissions for cleanup
