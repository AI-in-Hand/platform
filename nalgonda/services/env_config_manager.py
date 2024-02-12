from nalgonda.repositories.env_config_firestore_storage import EnvConfigFirestoreStorage
from nalgonda.services.env_vars_manager import ContextEnvVarsManager


class EnvConfigManager:
    """Manage environment variables.
    Incorporates the logic to get the environment variables from the Firestore.
    """

    def __init__(self, env_config_storage: EnvConfigFirestoreStorage):
        self.env_config_storage = env_config_storage

    def get_by_key(self, key: str) -> str:
        """Get the environment variable by key."""
        owner_id = ContextEnvVarsManager.get("owner_id")
        config = self.env_config_storage.get_config(owner_id)
        if not config:
            raise ValueError(f"Environment variables not set for the user: {owner_id}")
        value = config.get(key)
        if not value:
            raise ValueError(f"{key} not found for the given user.")
        return value
