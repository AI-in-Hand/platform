import logging

from backend.repositories.user_secret_storage import UserSecretStorage
from backend.services.encryption_service import EncryptionService
from backend.services.env_vars_manager import ContextEnvVarsManager
from backend.settings import settings

logger = logging.getLogger(__name__)


class UserSecretManager:
    """Manage user secrets. Incorporates the logic to get user secrets from the Firestore."""

    def __init__(self, user_secret_storage: UserSecretStorage):
        self._user_secret_storage = user_secret_storage
        self._encryption_service = EncryptionService(settings.encryption_key)

    def get_by_key(self, key: str) -> str:
        """Get a secret by key."""
        user_id = ContextEnvVarsManager.get("user_id")
        if not user_id:
            logger.error("user_id not found in the context variables.")
            raise ValueError("user_id not found in the context variables.")
        document = self._user_secret_storage.get_all_secrets(user_id) or {}
        value = document.get(key)
        if not value:
            logger.warning(f"Secret {key} not set for the given user.")
            raise ValueError(f"Secret {key} not set for the given user. Please set it first.")
        return self._encryption_service.decrypt(value)

    def set_by_key(self, key: str, value: str) -> None:
        """Set a secret by key."""
        user_id = ContextEnvVarsManager.get("user_id")
        if not user_id:
            logger.error("user_id not found in the context variables.")
            raise ValueError("user_id not found in the context variables.")
        secrets = self._user_secret_storage.get_all_secrets(user_id)
        if not secrets:
            secrets = {}
        secrets[key] = self._encryption_service.encrypt(value)
        self._user_secret_storage.set_secrets(user_id, secrets)

    def get_secret_names(self, user_id: str) -> list[str]:
        """Get the names of all the secrets for a user."""
        secrets = self._user_secret_storage.get_all_secrets(user_id)
        return list(secrets.keys()) if secrets else []

    def update_secrets(self, user_id: str, secrets: dict) -> None:
        encrypted_secrets = {key: self._encryption_service.encrypt(value) for key, value in secrets.items()}
        self._user_secret_storage.update_secrets(user_id, encrypted_secrets)
