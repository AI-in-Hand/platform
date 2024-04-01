import pytest

from backend.models.agent_flow_spec import AgentFlowSpec, AgentFlowSpecForAPI


@pytest.fixture
def agent_data():
    return {"type": "userproxy", "config": {"name": "example_name"}, "skills": ["skill1", "skill2"]}


@pytest.mark.parametrize("model", [AgentFlowSpec, AgentFlowSpecForAPI])
def test_skills_list_length(agent_data, model):
    agent_data["skills"] = [f"skill{i}" for i in range(11)]
    with pytest.raises(ValueError) as excinfo:
        model(**agent_data)
    assert "List should have at most 10 items after validation" in str(excinfo.value)
