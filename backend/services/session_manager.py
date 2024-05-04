from datetime import UTC, datetime
from http import HTTPStatus
from typing import Any

from agency_swarm import Agency
from fastapi import HTTPException

from backend.constants import DEFAULT_OPENAI_API_TIMEOUT
from backend.models.session_config import SessionConfig, SessionConfigForAPI
from backend.repositories.session_storage import SessionConfigStorage
from backend.services.adapters.session_adapter import SessionAdapter
from backend.services.oai_client import get_openai_client
from backend.services.user_variable_manager import UserVariableManager


class SessionManager:
    def __init__(
        self,
        session_storage: SessionConfigStorage,
        user_variable_manager: UserVariableManager,
        session_adapter: SessionAdapter,
    ):
        self.session_storage = session_storage
        self.user_variable_manager = user_variable_manager
        self.session_adapter = session_adapter
        self._openai_client = None

    @property
    def openai_client(self):
        """Lazily get the OpenAI client."""
        if self._openai_client is None:
            self._openai_client = get_openai_client(self.user_variable_manager)
        return self._openai_client

    def get_session(self, session_id: str) -> SessionConfig | None:
        """Return the session with the given ID."""
        return self.session_storage.load_by_id(session_id)

    def create_session(
        self, agency: Agency, name: str, agency_id: str, user_id: str, thread_ids: dict[str, Any]
    ) -> str:
        """Create a new session for the given agency and return its id."""
        session_id = agency.main_thread.id
        session_config = SessionConfig(
            id=session_id,
            name=name,
            user_id=user_id,
            agency_id=agency_id,
            thread_ids=thread_ids,
            timestamp=datetime.now(UTC).isoformat(),
        )
        self.session_storage.save(session_config)
        return session_id

    def rename_session(self, session_id: str, new_name: str) -> None:
        """Rename the session with the given ID."""
        self.session_storage.update(session_id, {"name": new_name})

    def update_session_timestamp(self, session_id: str) -> None:
        """Update the session with the given ID."""
        timestamp = datetime.now(UTC).isoformat()
        self.session_storage.update(session_id, {"timestamp": timestamp})

    def delete_session(self, session_id: str) -> None:
        """Delete the session with the given ID."""
        session_config = self.get_session(session_id)
        if session_config:
            main_thread_id: str = session_config.thread_ids.pop("main_thread")  # type: ignore
            self._delete_session_via_api(main_thread_id)
            for receiver in session_config.thread_ids.values():
                for thread_id in receiver.values():  # type: ignore
                    self._delete_session_via_api(thread_id)
            self.session_storage.delete(session_id)

    def _delete_session_via_api(self, session_id: str) -> None:
        """Delete the session with the given ID."""
        self.openai_client.beta.threads.delete(thread_id=session_id, timeout=DEFAULT_OPENAI_API_TIMEOUT)

    def delete_sessions_by_agency_id(self, agency_id: str) -> None:
        """Delete all sessions for the given agency."""
        sessions = self.session_storage.load_by_agency_id(agency_id)
        for session in sessions:
            self.delete_session(session.id)

    def get_sessions_for_user(self, user_id: str) -> list[SessionConfigForAPI]:
        """Return a list of all sessions for the given user."""
        sessions = self.session_storage.load_by_user_id(user_id)
        sessions_for_api = [self.session_adapter.to_api(session) for session in sessions]
        sorted_sessions = sorted(sessions_for_api, key=lambda x: x.timestamp, reverse=True)
        return sorted_sessions

    @staticmethod
    def validate_session_ownership(target_user_id: str, current_user_id: str) -> None:
        """Validate the ownership of the session."""
        if target_user_id != current_user_id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="You don't have permissions to access this session."
            )
