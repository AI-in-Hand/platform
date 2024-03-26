import instructor
import openai

from backend.services.env_config_manager import EnvConfigManager


def get_openai_client(env_config_manager: EnvConfigManager | None = None, api_key: str | None = None) -> openai.OpenAI:
    if not api_key:
        if not env_config_manager:
            raise ValueError("Either env_config_manager or api_key must be provided")
        api_key = env_config_manager.get_by_key("OPENAI_API_KEY")
    return instructor.patch(openai.OpenAI(api_key=api_key, max_retries=5))
