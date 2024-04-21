from backend.models.agency_config import AgencyConfig, AgencyConfigForAPI, CommunicationFlow
from backend.repositories.agent_flow_spec_storage import AgentFlowSpecStorage
from backend.services.adapters.agent_adapter import AgentAdapter


class AgencyAdapter:
    """
    Adapter for the AgencyConfig model. Transforms the data from the frontend format to the model and vice versa.
    In particular, it converts the `agents` field with a list of IDs (AgencyConfig Pydantic model)
    and main_agent and agency_chart fields with names of the agents into AgentFlowSpec objects in the `flows` field;
    and vice versa.
    """

    def __init__(self, agent_flow_spec_storage: AgentFlowSpecStorage, agent_adapter: AgentAdapter):
        self.agent_flow_spec_storage = agent_flow_spec_storage
        self.agent_adapter = agent_adapter

    @staticmethod
    def to_model(agency_config: AgencyConfigForAPI) -> AgencyConfig:
        """
        Converts the `sender` and `receiver` fields from AgencyConfigForAPI objects into fields:
        - `agents` with a list of IDs
        - `main_agent` and `agency_chart` with names of the agents.
        agency_chart has a form: {"0": [sender_name, receiver_name]}.
        """
        agents = []
        agency_chart = {}
        for i, flow in enumerate(agency_config.flows):
            sender_id = flow.sender.id
            agents.append(sender_id)
            if flow.receiver:
                receiver_id = flow.receiver.id
                agents.append(receiver_id)
                agency_chart[str(i)] = [flow.sender.config.name, flow.receiver.config.name]

        main_agent = agency_config.flows[0].sender.config.name if agency_config.flows else None

        agency_config_dict = agency_config.model_dump()
        agency_config_dict["agents"] = list(set(agents))  # Remove duplicates
        agency_config_dict["main_agent"] = main_agent
        agency_config_dict["agency_chart"] = agency_chart
        return AgencyConfig(**agency_config_dict)

    def to_api(self, agency_config: AgencyConfig) -> AgencyConfigForAPI:
        """
        Converts the `agents` field with a list of IDs (AgencyConfig Pydantic model)
        and main_agent and agency_chart fields with names of the agents into AgentFlowSpec objects in 2 fields:
        - main_agent (`sender` in the frontend)
        - agency_chart (`sender` + `receiver` in the frontend).
        Uses the agent_flow_spec_storage.load_by_ids method to get the AgentFlowSpec objects.
        The `receiver` field is optional.
        """
        if not agency_config.agents:
            return AgencyConfigForAPI(**agency_config.model_dump())

        agent_list = self.agent_flow_spec_storage.load_by_ids(agency_config.agents)
        agents = {agent.config.name: agent for agent in agent_list}

        flows = []
        for sender_name, receiver_name in agency_config.agency_chart.values():
            sender = agents[sender_name]
            receiver = agents[receiver_name] if receiver_name else None
            flow = CommunicationFlow(
                sender=self.agent_adapter.to_api(sender),
                receiver=self.agent_adapter.to_api(receiver) if receiver else None,
            )
            flows.append(flow)

        agency_config_dict = agency_config.model_dump()
        agency_config_dict["flows"] = flows
        return AgencyConfigForAPI(**agency_config_dict)
