from unittest.mock import MagicMock, patch

import pytest

from nalgonda.services.tool_service import ToolService, generate_tool_description


def test_generate_tool_description():
    with patch(
        "nalgonda.services.tool_service.get_chat_completion", return_value="Summary of the tool"
    ) as mock_get_chat:
        code = "def example(): pass"
        result = generate_tool_description(code)
        mock_get_chat.assert_called_once_with(
            system_message="""\
As a supportive assistant, ensure your responses are concise,
confined to a single sentence, and rigorously comply with the specified instructions.\
""",
            user_prompt="In one succinct sentence, describe the functionality of the tool provided below:\n```\n"
            + code
            + "\n```",
            temperature=0.0,
            model="gpt-3.5-turbo-1106",
        )
        assert result == "Summary of the tool", "The function did not return the expected summary"


def test_get_tool_class_found():
    tool_name = "SummarizeCode"
    with patch("nalgonda.services.tool_service.custom_tools.SummarizeCode", new_callable=MagicMock) as mock_tool:
        service = ToolService()
        result = service._get_tool_class(tool_name)
        assert result == mock_tool, "The function did not return the correct tool class"


def test_get_tool_class_not_found():
    tool_name = "NonExistingTool"
    service = ToolService()
    with pytest.raises(Exception) as exc_info:
        service._get_tool_class(tool_name)
    assert "Tool NonExistingTool not found" in str(exc_info.value), "The function did not raise the expected exception"


def test_get_tool_arguments():
    with patch("nalgonda.services.tool_service.get_chat_completion", return_value='{"arg": "value"}') as mock_get_chat:
        service = ToolService()
        result = service._get_tool_arguments("function_spec", "user_prompt")
        expected_args_str = '{"arg": "value"}'
        assert result == expected_args_str, "The function did not return the expected argument string"
        mock_get_chat.assert_called_once()


def test_execute_tool_success():
    tool_class_mock = MagicMock()
    tool_instance_mock = tool_class_mock.return_value
    tool_instance_mock.run.return_value = "Tool output"
    args = '{"arg":"value"}'

    with patch("nalgonda.services.tool_service.ToolService._get_tool_class", return_value=tool_class_mock):
        service = ToolService()
        result = service._execute_tool(tool_class_mock, args)
        assert result == "Tool output", "The function did not execute the tool correctly or failed to return its output"


def test_execute_tool_failure():
    tool_class_mock = MagicMock()
    tool_instance_mock = tool_class_mock.return_value
    tool_instance_mock.run.side_effect = Exception("Error running tool")
    args = '{"arg":"value"}'

    with patch("nalgonda.services.tool_service.ToolService._get_tool_class", return_value=tool_class_mock):
        service = ToolService()
        result = service._execute_tool(tool_class_mock, args)
        assert (
            "Error: Error running tool" in result
        ), "The function did not handle exceptions from tool execution properly"
