import logging

from backend.repositories.env_config_storage import EnvConfigStorage
from backend.services.encryption_service import EncryptionService
from backend.services.env_vars_manager import ContextEnvVarsManager
from backend.settings import settings

logger = logging.getLogger(__name__)


class EnvConfigManager:
    """Manage environment variables.
    Incorporates the logic to get the environment variables from the Firestore.
    """

    def __init__(self, env_config_storage: EnvConfigStorage):
        self._env_config_storage = env_config_storage
        self._encryption_service = EncryptionService(settings.encryption_key)

    def get_by_key(self, key: str) -> str:
        """Get the environment variable by key."""
        user_id = ContextEnvVarsManager.get("user_id")
        if not user_id:
            logger.error("user_id not found in the environment variables.")
            raise ValueError("user_id not found in the environment variables.")
        config = self._env_config_storage.get_config(user_id)
        if not config:
            logger.warning(f"Environment variables not set for the user: {user_id}")
            raise ValueError(f"Environment variables not set for the user: {user_id}")
        value = config.get(key)
        if not value:
            logger.warning(f"{key} not found for the given user.")
            raise ValueError(f"{key} not found for the given user.")
        return self._encryption_service.decrypt(value)

    def set_by_key(self, key: str, value: str) -> None:
        """Set the environment variable by key."""
        user_id = ContextEnvVarsManager.get("user_id")
        if not user_id:
            logger.error("user_id not found in the environment variables.")
            raise ValueError("user_id not found in the environment variables.")
        config = self._env_config_storage.get_config(user_id)
        if not config:
            config = {}
        config[key] = self._encryption_service.encrypt(value)
        self._env_config_storage.set_config(user_id, config)

    def get_config_keys(self, user_id: str) -> list[str]:
        """Get the environment variables for the user. Return the keys only."""
        config = self._env_config_storage.get_config(user_id)
        return list(config.keys()) if config else []

    def update_config(self, user_id: str, env_config: dict) -> None:
        encrypted_config = {key: self._encryption_service.encrypt(value) for key, value in env_config.items()}
        self._env_config_storage.update_config(user_id, encrypted_config)
