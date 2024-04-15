from unittest.mock import MagicMock, patch

import pytest

from backend.services.skill_service import SkillService


def test_get_skill_class_found():
    skill_name = "SummarizeCode"
    with patch("backend.services.skill_service.custom_skills.SummarizeCode", new_callable=MagicMock) as mock_skill:
        service = SkillService()
        result = service._get_skill_class(skill_name)
        assert result == mock_skill, "The function did not return the correct skill class"


def test_get_skill_class_not_found():
    skill_name = "NonExistingSkill"
    service = SkillService()
    with pytest.raises(Exception) as exc_info:
        service._get_skill_class(skill_name)
    assert "Skill NonExistingSkill not found" in str(
        exc_info.value
    ), "The function did not raise the expected exception"


def test_get_skill_arguments():
    with patch("backend.services.skill_service.get_chat_completion", return_value='{"arg": "value"}') as mock_get_chat:
        service = SkillService()
        result = service._get_skill_arguments("function_spec", "user_prompt")
        expected_args_str = '{"arg": "value"}'
        assert result == expected_args_str, "The function did not return the expected argument string"
        mock_get_chat.assert_called_once()


def test_execute_skill_success():
    skill_class_mock = MagicMock()
    skill_instance_mock = skill_class_mock.return_value
    skill_instance_mock.run.return_value = "Skill output"
    args = '{"arg":"value"}'

    with patch("backend.services.skill_service.SkillService._get_skill_class", return_value=skill_class_mock):
        service = SkillService()
        result = service._execute_skill(skill_class_mock, args)
        assert (
            result == "Skill output"
        ), "The function did not execute the skill correctly or failed to return its output"


def test_execute_skill_failure():
    skill_class_mock = MagicMock()
    skill_instance_mock = skill_class_mock.return_value
    skill_instance_mock.run.side_effect = Exception("Error running skill")
    args = '{"arg":"value"}'

    with patch("backend.services.skill_service.SkillService._get_skill_class", return_value=skill_class_mock):
        service = SkillService()
        result = service._execute_skill(skill_class_mock, args)
        assert (
            "Error: Error running skill" in result
        ), "The function did not handle exceptions from skill execution properly"
