import instructor
import openai

from backend.services.user_secret_manager import UserSecretManager


def get_openai_client(
    user_secret_manager: UserSecretManager | None = None, api_key: str | None = None
) -> openai.OpenAI:
    if not api_key:
        if not user_secret_manager:
            raise ValueError("Either user_secret_manager or api_key must be provided")
        api_key = user_secret_manager.get_by_key("OPENAI_API_KEY")
    return instructor.patch(openai.OpenAI(api_key=api_key, max_retries=5))
