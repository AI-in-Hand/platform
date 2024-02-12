import instructor
import openai

from nalgonda.repositories.env_config_firestore_storage import EnvConfigFirestoreStorage
from nalgonda.services.env_config_manager import EnvConfigManager


def get_openai_client(env_config_storage: EnvConfigFirestoreStorage):
    api_key = EnvConfigManager(env_config_storage).get_by_key("OPENAI_API_KEY")
    return instructor.patch(openai.OpenAI(api_key=api_key, max_retries=5))
