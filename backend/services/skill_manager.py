import logging
from datetime import UTC, datetime
from http import HTTPStatus

from fastapi import HTTPException

from backend.models.skill_config import SkillConfig
from backend.repositories.skill_config_storage import SkillConfigStorage

logger = logging.getLogger(__name__)


class SkillManager:
    def __init__(self, storage: SkillConfigStorage):
        self.storage = storage

    def get_skill_list(self, current_user_id: str) -> list[SkillConfig]:
        """Get a list of configs for all skills."""
        return self.storage.load_by_user_id(current_user_id) + self.storage.load_by_user_id(None)

    def get_skill_config(self, id_: str) -> SkillConfig:
        """Get a skill configuration by ID."""
        config_db = self.storage.load_by_id(id_)
        if not config_db:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Skill not found")
        return config_db

    def create_skill_version(self, config: SkillConfig, current_user_id: str) -> tuple[str, int]:
        """Create a new version of the skill configuration.
        NOTE: currently this endpoint is not fully supported.
        """
        config_db = None

        # support template configs:
        if not config.user_id:
            config.id = None
        # check if the current_user has permissions
        if config.id:
            config_db = self.get_skill_config(config.id)
            self.check_user_permissions(config_db, current_user_id)

        # Ensure the skill is associated with the current user
        config.user_id = current_user_id

        config.version = config_db.version + 1 if config_db else 1
        config.approved = False
        config.timestamp = datetime.now(UTC).isoformat()

        skill_id, skill_version = self.storage.save(config)
        return skill_id, skill_version

    def delete_skill(self, id_: str, current_user_id: str) -> None:
        """Delete a skill configuration."""
        config = self.get_skill_config(id_)
        self.check_user_permissions(config, current_user_id)
        self.storage.delete(id_)

    @staticmethod
    def check_user_permissions(config: SkillConfig, current_user_id: str) -> None:
        if config.user_id != current_user_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="You don't have permissions to access this skill"
            )
