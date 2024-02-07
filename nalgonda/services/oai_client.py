import instructor
import openai

from nalgonda.repositories.env_config_firestore_storage import EnvConfigFirestoreStorage
from nalgonda.services.env_vars_manager import ContextEnvVarsManager

env_config_storage = EnvConfigFirestoreStorage()


def get_openai_client():
    owner_id = ContextEnvVarsManager.get("owner_id")
    config = env_config_storage.get_config(owner_id)
    api_key = config["OPENAI_API_KEY"]
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found for the given owner_id.")
    return instructor.patch(openai.OpenAI(api_key=api_key, max_retries=5))
