import instructor
import openai

from backend.services.user_variable_manager import UserVariableManager


def get_openai_client(
    user_variable_manager: UserVariableManager | None = None, api_key: str | None = None
) -> openai.OpenAI:
    if not api_key:
        if not user_variable_manager:
            raise ValueError("Either user_variable_manager or api_key must be provided")
        api_key = user_variable_manager.get_by_key("OPENAI_API_KEY")
    return instructor.patch(openai.OpenAI(api_key=api_key, max_retries=5))
