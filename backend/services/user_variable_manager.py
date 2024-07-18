import logging

from backend.exceptions import UnsetVariableError
from backend.repositories.agent_flow_spec_storage import AgentFlowSpecStorage
from backend.repositories.user_variable_storage import UserVariableStorage
from backend.services.context_vars_manager import ContextEnvVarsManager
from backend.services.encryption_service import EncryptionService
from backend.settings import settings

logger = logging.getLogger(__name__)


class UserVariableManager:
    """Manage user variables. Incorporates the logic for setting, getting, and updating user variables"""

    DEFAULT_VARIABLE_NAMES: set[str] = {"OPENAI_API_KEY"}

    def __init__(self, user_variable_storage: UserVariableStorage, agent_storage: AgentFlowSpecStorage):
        self._user_variable_storage = user_variable_storage
        self._encryption_service = EncryptionService(settings.encryption_key)
        self._agent_storage = agent_storage

    def get_by_key(self, key: str) -> str:
        """Get a variable by key."""
        user_id = ContextEnvVarsManager.get("user_id")
        if not user_id:
            logger.error("user_id not found in the context variables.")
            raise ValueError("user_id not found in the context variables.")
        document = self._user_variable_storage.get_all_variables(user_id) or {}
        value = document.get(key)
        if not value:
            raise UnsetVariableError(key=key)
        return self._encryption_service.decrypt(value)

    def set_by_key(self, key: str, value: str) -> None:
        """Set a variable by key."""
        user_id = ContextEnvVarsManager.get("user_id")
        if not user_id:
            logger.error("user_id not found in the context variables.")
            raise ValueError("user_id not found in the context variables.")
        variables = self._user_variable_storage.get_all_variables(user_id)
        if not variables:
            variables = {}
        variables[key] = self._encryption_service.encrypt(value)
        self._user_variable_storage.set_variables(user_id, variables)

    def get_variable_names(self, user_id: str) -> list[str]:
        """Get the names of all the variables for a user."""
        variables = self._user_variable_storage.get_all_variables(user_id)
        variable_names = set(variables.keys()) if variables else set()
        # Combine user's variables with the default ones and sort them
        all_variables = variable_names.union(self.DEFAULT_VARIABLE_NAMES)
        return sorted(all_variables)

    def create_or_update_variables(self, user_id: str, variables: dict[str, str]) -> bool:
        """Update or create variables for a user.
        :param user_id: The ID of the user whose variables are being updated.
        :param variables: A dictionary containing the variables to be updated or created.
                        The dictionary may contain the following types of changes:
            - Removed keys: If a key is missing, it will be removed from the variables.
            - New/updated keys: If the value is not an empty string, the value will be encrypted and updated.
            - Unchanged keys: If the value is an empty string, the value will not be updated.
        """
        existing_variables = self._user_variable_storage.get_all_variables(user_id) or {}

        # Encrypt and update new or changed variables
        for key, value in variables.items():
            if value:  # Only update if the value is not an empty string
                if key == "OPENAI_API_KEY" and value != self._encryption_service.decrypt(existing_variables[key]):  # Check if OPENAI_API_KEY is updated
                    agents = self._agent_storage.load_by_user_id(user_id=user_id)
                    if len(agents) > 0:  # Check if this user has any agent
                        return False

                existing_variables[key] = self._encryption_service.encrypt(value)

        # Remove variables that are no longer present
        keys_to_remove = set(existing_variables) - set(variables)
        for key in keys_to_remove:
            del existing_variables[key]

        self._user_variable_storage.set_variables(user_id, existing_variables)
        return True
