from datetime import UTC, datetime
from typing import Any

from agency_swarm import Agency

from backend.models.session_config import SessionConfig
from backend.repositories.session_storage import SessionConfigStorage
from backend.services.user_secret_manager import UserSecretManager


class SessionManager:
    def __init__(self, session_storage: SessionConfigStorage, user_secret_manager: UserSecretManager):
        self.user_secret_manager = user_secret_manager
        self.session_storage = session_storage

    def get_session(self, session_id: str) -> SessionConfig | None:
        """Return the session with the given ID."""
        return self.session_storage.load_by_id(session_id)

    def create_session(self, agency: Agency, agency_id: str, user_id: str, thread_ids: dict[str, Any]) -> str:
        """Create a new session for the given agency and return its id."""
        session_id = agency.main_thread.id
        session_config = SessionConfig(
            id=session_id,
            user_id=user_id,
            agency_id=agency_id,
            thread_ids=thread_ids,
            timestamp=datetime.now(UTC).isoformat(),
        )
        self.session_storage.save(session_config)
        return session_id

    def delete_session(self, session_id: str) -> None:
        """Delete the session with the given ID."""
        self.session_storage.delete(session_id)
