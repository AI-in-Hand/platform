from pathlib import Path
from unittest.mock import mock_open, patch

from nalgonda.constants import AGENCY_DATA_DIR
from nalgonda.custom_tools.write_and_save_program import File, WriteAndSaveProgram


@patch("builtins.open", new_callable=mock_open)
@patch("pathlib.Path.mkdir")
def test_write_and_save_program_with_valid_files(mock_mkdir, mock_file):
    files = [
        File(file_name="test1.py", body='print("Hello")', chain_of_thought=""),
        File(file_name="test2.py", body='print("World")', chain_of_thought=""),
    ]
    save_program_tool = WriteAndSaveProgram(files=files, chain_of_thought="")
    response = save_program_tool.run()
    expected_path1 = Path(AGENCY_DATA_DIR / "test_agency_id" / "test1.py").as_posix()
    expected_path2 = Path(AGENCY_DATA_DIR / "test_agency_id" / "test2.py").as_posix()
    assert "File written to " + expected_path1 in response
    assert "File written to " + expected_path2 in response
    mock_file.assert_called()
    mock_mkdir.assert_called()


@patch("builtins.open", new_callable=mock_open)
def test_write_and_save_program_with_invalid_path(mock_file):
    files = [File(file_name="../invalid/path.py", body='print("Fail")', chain_of_thought="")]
    save_program_tool = WriteAndSaveProgram(files=files, chain_of_thought="")
    response = save_program_tool.run()
    assert "Invalid file path" in response
    mock_file.assert_not_called()
