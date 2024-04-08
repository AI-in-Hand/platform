import logging

from backend.repositories.user_secret_storage import UserSecretStorage
from backend.services.context_vars_manager import ContextEnvVarsManager
from backend.services.encryption_service import EncryptionService
from backend.settings import settings

logger = logging.getLogger(__name__)


class UserSecretManager:
    """Manage user secrets. Incorporates the logic for setting, getting, and updating user secrets."""

    DEFAULT_SECRET_NAMES: set[str] = {"OPENAI_API_KEY"}

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
        secret_names = set(secrets.keys()) if secrets else set()
        # Combine user's secrets with the default ones and sort them
        all_secrets = secret_names.union(self.DEFAULT_SECRET_NAMES)
        return sorted(all_secrets)

    def update_or_create_secrets(self, user_id: str, secrets: dict[str, str]) -> None:
        """Update or create secrets for a user.
        :param user_id: The ID of the user whose secrets are being updated.
        :param secrets: A dictionary containing the secrets to be updated or created.
                        The dictionary may contain the following types of changes:
            - Removed keys: If a key is missing, it will be removed from the secrets.
            - New/updated keys: If the value is not an empty string, the value will be encrypted and updated.
            - Unchanged keys: If the value is an empty string, the value will not be updated.
        """
        existing_secrets = self._user_secret_storage.get_all_secrets(user_id) or {}

        # Encrypt and update new or changed secrets
        for key, value in secrets.items():
            if value:  # Only update if the value is not an empty string
                existing_secrets[key] = self._encryption_service.encrypt(value)

        # Remove secrets that are no longer present
        keys_to_remove = set(existing_secrets) - set(secrets)
        for key in keys_to_remove:
            del existing_secrets[key]

        self._user_secret_storage.set_secrets(user_id, existing_secrets)
