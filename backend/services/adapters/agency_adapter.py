from backend.models.agency_config import AgencyConfig, AgencyConfigForAPI
from backend.repositories.agent_flow_spec_storage import AgentFlowSpecStorage
from backend.services.adapters.agent_adapter import AgentAdapter


class AgencyAdapter:
    """
    Adapter for the AgencyConfig model. Transforms the data from the frontend format to the model and vice versa.
    In particular, it converts the `agents` field with a list of IDs (AgencyConfig Pydantic model)
    and main_agent and agency_chart fields with names of the agents into AgentFlowSpec objects in 2 fields:
    - main_agent (`sender` in the frontend)
    - agency_chart (`sender` + `receiver` in the frontend);
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
        agency_chart has a form: {0: [sender_name, receiver_name]}.
        """
        sender = [agency_config.sender.id] if agency_config.sender else []
        receiver = [agency_config.receiver.id] if agency_config.receiver else []
        agents = sender + receiver
        # TODO: support multiple rows in the agency_chart (not implemented in the frontend)
        agency_chart = (
            {0: [agency_config.sender.config.name, agency_config.receiver.config.name]}
            if agency_config.sender and agency_config.receiver
            else {}
        )

        agency_config_dict = agency_config.model_dump()
        agency_config_dict["agents"] = agents
        agency_config_dict["main_agent"] = agency_config.sender.config.name if agency_config.sender else None
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
        sender = agents[agency_config.main_agent] if agency_config.main_agent else None
        receiver = agents[agency_config.agency_chart[0][1]] if agency_config.agency_chart else None

        agency_config_dict = agency_config.model_dump()
        agency_config_dict["sender"] = self.agent_adapter.to_api(sender) if sender else None
        agency_config_dict["receiver"] = self.agent_adapter.to_api(receiver) if receiver else None
        return AgencyConfigForAPI(**agency_config_dict)
