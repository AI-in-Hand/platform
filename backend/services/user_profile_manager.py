import logging

from backend.repositories.user_profile_storage import UserProfileStorage

logger = logging.getLogger(__name__)


class UserProfileManager:
    """Manage user profile data. Incorporates the logic for setting, getting, and updating user profile data"""

    def __init__(self, user_profile_storage: UserProfileStorage):
        self._user_profile_storage = user_profile_storage

    def get_user_profile(self, user_id: str) -> dict | None:
        """Get the profile data for a user."""
        return self._user_profile_storage.get_profile(user_id)

    def update_user_profile(self, user_id: str, fields: dict[str, str]) -> None:
        """Set profile data for a user.
        :param user_id: The ID of the user whose variables are being updated.
        :param fields: A dictionary containing the key and value to be updated or created.
        """
        existing_fields = self._user_profile_storage.get_profile(user_id) or {}

        for key, value in fields.items():
            if value:  # Only update if the value is not an empty string
                existing_fields[key] = value

        self._user_profile_storage.update_profile(user_id, existing_fields)
