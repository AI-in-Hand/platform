from backend.models.agency_config import AgencyConfig, AgencyConfigForAPI
from backend.repositories.agent_flow_spec_firestore_storage import AgentFlowSpecFirestoreStorage


class AgencyConfigAdapter:
    """
    Adapter for the AgencyConfig model. Transforms the data from the frontend format to the model and vice versa.
    In particular, it converts the `agents` field with a list of IDs (AgencyConfig Pydantic model)
    and main_agent and agency_chart fields with names of the agents into AgentFlowSpec objects in 2 fields:
    - main_agent (`sender` in the frontend)
    - agency_chart (`sender` + `receiver` in the frontend);
    and vice versa.
    """

    def __init__(self, agent_flow_spec_storage: AgentFlowSpecFirestoreStorage):
        self.agent_flow_spec_storage = agent_flow_spec_storage

    @staticmethod
    def to_model(agency_config: AgencyConfigForAPI) -> AgencyConfig:
        """
        Converts the `sender` and `receiver` fields from AgencyConfigForAPI objects into fields:
        - `agents` with a list of IDs
        - `main_agent` and `agency_chart` with names of the agents.
        agency_chart has a form: [[sender, receiver], ...]
        """
        agents = [agency_config.sender.id] + ([agency_config.receiver.id] if agency_config.receiver else [])
        agency_chart = (
            [[agency_config.sender.config.name, agency_config.receiver.config.name]] if agency_config.receiver else []
        )

        agency_config_dict = agency_config.model_dump()
        agency_config_dict["agents"] = agents
        agency_config_dict["main_agent"] = agency_config.sender.config.name
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
        agent_list = self.agent_flow_spec_storage.load_by_ids(agency_config.agents)
        agents = {agent.config.name: agent for agent in agent_list}
        sender = agents[agency_config.main_agent] if agency_config.main_agent else None
        receiver = agents[agency_config.agency_chart[0][1]] if agency_config.agency_chart else None

        agency_config_dict = agency_config.model_dump()
        agency_config_dict["sender"] = sender
        agency_config_dict["receiver"] = receiver
        return AgencyConfigForAPI(**agency_config_dict)
