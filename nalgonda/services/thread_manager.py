from agency_swarm import Agency, Agent, get_openai_client
from agency_swarm.threads import Thread


class ThreadManager:
    def create_threads(self, agency: Agency) -> str:
        """Create new threads for the given agency and return the thread ID of the main thread."""
        client = get_openai_client()
        self._init_threads(agency, client)
        agency.main_thread = self._create_thread(agency.user, agency.ceo, client)
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
