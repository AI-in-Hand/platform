from backend.models.agent_flow_spec import AgentConfig, AgentFlowSpec, AgentFlowSpecForAPI
from backend.models.skill_config import SkillConfig


def test_to_model(agent_adapter):
    skill_configs = [
        SkillConfig(title="Skill 1"),
        SkillConfig(title="Skill 2"),
    ]
    agent_flow_spec_api = AgentFlowSpecForAPI(
        id="1234",
        type="assistant",
        config=AgentConfig(name="Test Agent"),
        skills=skill_configs,
        description="Test Description",
    )

    agent_flow_spec = agent_adapter.to_model(agent_flow_spec_api)

    assert agent_flow_spec.type == "assistant"
    assert agent_flow_spec.config.name == "Test Agent"
    assert agent_flow_spec.skills == ["Skill 1", "Skill 2"]
    assert agent_flow_spec.description == "Test Description"


def test_to_api(agent_adapter, mocker):
    skill_configs = [
        SkillConfig(title="Skill 1"),
        SkillConfig(title="Skill 2"),
    ]
    agent_flow_spec = AgentFlowSpec(
        id="1234",
        type="assistant",
        config=AgentConfig(name="Test Agent"),
        skills=["Skill 1", "Skill 2"],
        description="Test Description",
    )

    mocker.patch.object(
        agent_adapter.skill_config_storage,
        "load_by_titles",
        return_value=skill_configs,
    )

    agent_flow_spec_api = agent_adapter.to_api(agent_flow_spec)

    assert agent_flow_spec_api.type == "assistant"
    assert agent_flow_spec_api.config.name == "Test Agent"
    assert agent_flow_spec_api.skills == skill_configs
    assert agent_flow_spec_api.description == "Test Description"


def test_to_api_without_skills(agent_adapter):
    agent_flow_spec = AgentFlowSpec(
        id="1234",
        type="assistant",
        config=AgentConfig(name="Test Agent"),
        skills=[],
        description="Test Description",
    )

    agent_flow_spec_api = agent_adapter.to_api(agent_flow_spec)

    assert agent_flow_spec_api.type == "assistant"
    assert agent_flow_spec_api.config.name == "Test Agent"
    assert agent_flow_spec_api.skills == []
    assert agent_flow_spec_api.description == "Test Description"
