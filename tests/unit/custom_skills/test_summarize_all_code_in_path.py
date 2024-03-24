from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from nalgonda.custom_skills import SummarizeAllCodeInPath


@pytest.fixture
def mock_openai_response():
    class MockCompletion:
        message = Mock(content="Summary of the code")

    class MockOpenAIResponse:
        choices = [MockCompletion()]

    return MockOpenAIResponse()


@patch("nalgonda.utils.get_openai_client")
def test_summarize_all_code_in_path_with_valid_codebase(mock_openai_client, mock_openai_response, tmp_path):
    # Create a simple Python file
    (tmp_path / "test.py").write_text('print("Hello, World!")')
    mock_openai_client.return_value.chat.completions.create.return_value = mock_openai_response

    summarize_skill = SummarizeAllCodeInPath(start_path=Path(tmp_path))
    results = summarize_skill.run()
    assert "Summary of the code" in results
    mock_openai_client.assert_called_once()


@patch("nalgonda.utils.get_openai_client", side_effect=Exception("API failed"))
def test_summarize_all_code_in_path_with_api_failure(mock_openai_client, tmp_path):
    # Create a simple Python file
    (tmp_path / "test.py").write_text('print("Hello, World!")')
    summarize_skill = SummarizeAllCodeInPath(start_path=Path(tmp_path))
    with pytest.raises(Exception) as exc_info:
        summarize_skill.run()
    assert "API failed" in str(exc_info.value)
    mock_openai_client.assert_called_once()
