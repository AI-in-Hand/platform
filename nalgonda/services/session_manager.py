from datetime import datetime

from agency_swarm import Agency, Agent
from agency_swarm.threads import Thread

from nalgonda.models.session_config import SessionConfig
from nalgonda.repositories.env_config_firestore_storage import EnvConfigFirestoreStorage
from nalgonda.repositories.session_firestore_storage import SessionConfigFirestoreStorage
from nalgonda.services.oai_client import get_openai_client


class SessionManager:
    def __init__(self, session_storage: SessionConfigFirestoreStorage, env_config_storage: EnvConfigFirestoreStorage):
        self.env_config_storage = env_config_storage
        self.session_storage = session_storage

    def create_session(self, agency: Agency, agency_id: str, owner_id: str) -> str:
        """Create a new session for the given agency and return its id."""
        session_id = self._create_threads(agency)
        session_config = SessionConfig(
            session_id=session_id,
            owner_id=owner_id,
            agency_id=agency_id,
            created_at=int(datetime.utcnow().timestamp()),
        )
        self.session_storage.save(session_config)
        return session_id

    def _create_threads(self, agency: Agency) -> str:
        """Create new threads for the given agency and return the thread ID of the main thread."""
        client = get_openai_client(self.env_config_storage)
        self._init_threads(agency, client)
        return agency.main_thread.id

    def _init_threads(self, agency: Agency, client) -> None:
        """
        Initializes threads for communication between agents within the agency.
        See agency_swarm.agency.Agency._init_threads for more details.

        :param agency: The agency for which threads are to be initialized.
        :param client: The OpenAI client object.
        """
        for sender, recipients in agency.agents_and_threads.items():
            for recipient in recipients:
                agency.agents_and_threads[sender][recipient] = self._create_thread(
                    agency.agents[sender],
                    agency.agents[recipient],
                    client,
                )
        agency.main_thread = self._create_thread(agency.user, agency.ceo, client)

    def _create_thread(self, agent: Agent, recipient_agent: Agent, client) -> Thread:
        """
        Creates a new thread for communication between the agent and the recipient_agent.

        :param agent: The agent that is to be the sender of messages in the thread.
        :param recipient_agent: The agent that is to be the recipient of messages in the thread.

        :return: The newly created Thread object.
        """
        new_thread = client.beta.threads.create()
        thread = Thread(agent, recipient_agent)
        thread.thread = new_thread
        thread.id = new_thread.id
        return thread
