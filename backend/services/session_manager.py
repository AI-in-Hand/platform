from datetime import UTC, datetime
from http import HTTPStatus
from typing import Any

from agency_swarm import Agency
from fastapi import HTTPException

from backend.models.session_config import SessionConfig, SessionConfigForAPI
from backend.repositories.agency_config_storage import AgencyConfigStorage
from backend.repositories.session_storage import SessionConfigStorage
from backend.services.adapters.session_adapter import SessionAdapter
from backend.services.user_secret_manager import UserSecretManager


class SessionManager:
    def __init__(
        self,
        session_storage: SessionConfigStorage,
        agency_storage: AgencyConfigStorage,
        user_secret_manager: UserSecretManager,
        session_adapter: SessionAdapter,
    ):
        self.session_storage = session_storage
        self.agency_storage = agency_storage
        self.user_secret_manager = user_secret_manager
        self.session_adapter = session_adapter

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

    def delete_sessions_by_agency_id(self, agency_id: str) -> None:
        """Delete all sessions for the given agency."""
        self.session_storage.delete_by_agency_id(agency_id)

    def get_sessions_for_user(self, user_id: str) -> list[SessionConfigForAPI]:
        """Return a list of all sessions for the given user."""
        sessions = self.session_storage.load_by_user_id(user_id)
        sessions_for_api = [self.session_adapter.to_api(session) for session in sessions]
        sorted_sessions = sorted(sessions_for_api, key=lambda x: x.timestamp, reverse=True)
        return sorted_sessions

    def validate_agency_permissions(self, agency_id: str, user_id: str) -> None:
        """Validate if the user has permissions to access the agency."""
        agency_config_db = self.agency_storage.load_by_id(agency_id)
        if not agency_config_db:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Agency not found")
        if agency_config_db.user_id != user_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="You don't have permissions to access this agency"
            )
