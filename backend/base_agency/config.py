from agency_swarm import Agency, Agent
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from constants import CONFIG_FILE, DEFAULT_CONFIG_FILE
from custom_tools import TOOL_MAPPING

LATEST_GPT_MODEL = "gpt-4-1106-preview"


class Settings(BaseSettings):
    openai_api_key: str = Field(validation_alias="OPENAI_API_KEY")
    gpt_model: str = Field(default=LATEST_GPT_MODEL, validation_alias="GPT_MODEL")

    model_config = SettingsConfigDict()


settings = Settings()


class AgentConfig(BaseModel):
    """Config for an agent"""

    id: str | None = None
    role: str
    description: str
    instructions: str
    files_folder: str | None = None
    tools: list[str] = Field(default_factory=list)


class AppConfig(BaseModel):
    """Config for the agency"""

    agency_manifesto: str = Field(default="Agency Manifesto")
    agents: list[AgentConfig]
    agency_chart: list[str | list[str]]  # contains agent roles


def load_agency_from_config(agency_id: str) -> Agency:
    """Load the agency from the config file"""

    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            config = AppConfig.model_validate_json(f.read())
    else:
        with open(DEFAULT_CONFIG_FILE) as f:
            config = AppConfig.model_validate_json(f.read())

    agents = {
        agent_conf.role: Agent(
            id=agent_conf.id,
            name=f"{agent_conf.role}_{agency_id}",
            description=agent_conf.description,
            instructions=agent_conf.instructions,
            files_folder=agent_conf.files_folder,
            tools=[TOOL_MAPPING[tool] for tool in agent_conf.tools if tool in TOOL_MAPPING],
        )
        for agent_conf in config.agents
    }

    # Create agency chart based on the config
    agency_chart = [
        [agents[role] for role in chart] if isinstance(chart, list) else agents[chart] for chart in config.agency_chart
    ]

    agency = Agency(agency_chart, shared_instructions=config.agency_manifesto)

    update_agent_ids_in_config(agency_id, agency.agents, config)

    return agency


def update_agent_ids_in_config(agency_id: str, agents: list[Agent], config: AppConfig):
    """Update the agent IDs in the config file"""
    for agent in agents:
        for agent_conf in config.agents:
            if agent.name == f"{agent_conf.role}_{agency_id}":
                agent_conf.id = agent.id
                break

    # Save the config file
    with open(CONFIG_FILE, "w") as f:
        f.write(config.model_dump_json(indent=2))
