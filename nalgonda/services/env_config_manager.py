import logging

from nalgonda.repositories.env_config_firestore_storage import EnvConfigFirestoreStorage
from nalgonda.services.env_vars_manager import ContextEnvVarsManager

logger = logging.getLogger(__name__)


class EnvConfigManager:
    """Manage environment variables.
    Incorporates the logic to get the environment variables from the Firestore.
    """

    def __init__(self, env_config_storage: EnvConfigFirestoreStorage):
        self.env_config_storage = env_config_storage

    def get_by_key(self, key: str) -> str:
        """Get the environment variable by key."""
        owner_id = ContextEnvVarsManager.get("owner_id")
        if not owner_id:
            logger.error("owner_id not found in the environment variables.")
            raise ValueError("owner_id not found in the environment variables.")
        config = self.env_config_storage.get_config(owner_id)
        if not config:
            logger.warning(f"Environment variables not set for the user: {owner_id}")
            raise ValueError(f"Environment variables not set for the user: {owner_id}")
        value = config.get(key)
        if not value:
            logger.warning(f"{key} not found for the given user.")
            raise ValueError(f"{key} not found for the given user.")
        return value
