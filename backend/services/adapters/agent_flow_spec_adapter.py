from backend.models.agent_flow_spec import AgentFlowSpec, AgentFlowSpecForAPI
from backend.repositories.skill_config_firestore_storage import SkillConfigFirestoreStorage


class AgentFlowSpecAdapter:
    """
    Adapter for AgentFlowSpec. Transforms the data from the frontend format to the model and vice versa.
    In particular, it converts the `skills` field from a list of strings (model)
    to a list of SkillConfig objects (frontend) and vice versa.
    """

    def __init__(self, skill_config_storage: SkillConfigFirestoreStorage):
        self.skill_config_storage = skill_config_storage

    @staticmethod
    def to_model(agent_flow_spec: AgentFlowSpecForAPI) -> AgentFlowSpec:
        """
        Converts the `skills` field from a list of SkillConfig objects to a list of strings.
        """
        skill_names = [skill.title for skill in agent_flow_spec.skills]

        agent_flow_spec_dict = agent_flow_spec.dict()
        agent_flow_spec_dict["skills"] = skill_names
        return AgentFlowSpec.model_validate(agent_flow_spec_dict)

    def to_api(self, agent_flow_spec: AgentFlowSpec) -> AgentFlowSpecForAPI:
        """
        Converts the `skills` field from a list of strings to a list of SkillConfig objects.
        """
        skill_configs = self.skill_config_storage.load_by_titles(agent_flow_spec.skills)

        agent_flow_spec_dict = agent_flow_spec.dict()
        agent_flow_spec_dict["skills"] = skill_configs
        agent_flow_spec_new = AgentFlowSpecForAPI.model_validate(agent_flow_spec_dict)
        return agent_flow_spec_new
