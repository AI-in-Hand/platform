from datetime import UTC, datetime

from backend.models.message import Message
from backend.services.oai_client import get_openai_client
from backend.services.user_variable_manager import UserVariableManager


class MessageManager:
    def __init__(self, user_variable_manager: UserVariableManager):
        self.user_variable_manager = user_variable_manager
        self._openai_client = None

    @property
    def openai_client(self):
        """Lazily get the OpenAI client."""
        if self._openai_client is None:
            self._openai_client = get_openai_client(self.user_variable_manager)
        return self._openai_client

    def get_messages(self, session_id: str, limit: int = 20, before: str | None = None) -> list[Message]:
        """Get the list of messages for the given session_id."""
        messages = self.openai_client.beta.threads.messages.list(
            thread_id=session_id,
            limit=limit,
            before=before,
            order="asc",
        )
        messages_output = [
            Message(
                id=message.id,
                content=message.content[0].text.value
                if message.content and message.content[0].text
                else "[No content]",
                role=message.role,
                timestamp=datetime.fromtimestamp(message.created_at, tz=UTC).isoformat(),
                session_id=session_id,
            )
            for message in messages
        ]
        return messages_output
