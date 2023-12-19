from agency_swarm import Agent
from pydantic import BaseModel, Field

from nalgonda.models.agent_config import AgentConfig
from nalgonda.persistence.agency_config_file_storage import AgencyConfigFileStorage


class AgencyConfig(BaseModel):
    """Agency configuration model"""

    agency_id: str = Field(...)
    agency_manifesto: str = Field(default="Agency Manifesto")
    agents: list[AgentConfig] = Field(...)
    agency_chart: list[str | list[str]] = Field(...)  # contains agent roles

    def update_agent_ids_in_config(self, agents: list[Agent]) -> None:
        """Update agent ids in config with the ids of the agents in the swarm"""
        for agent in agents:
            for agent_config in self.agents:
                if agent.name == f"{agent_config.role}_{self.agency_id}":
                    agent_config.id = agent.id

    @classmethod
    def load(cls, agency_id: str) -> "AgencyConfig":
        """Load agency config from the storage"""
        with AgencyConfigFileStorage(agency_id) as config_file:
            config = config_file.load()

        config["agency_id"] = agency_id
        return cls.model_validate(config)

    def save(self) -> None:
        """Save agency config to the storage"""
        with AgencyConfigFileStorage(self.agency_id) as config_file:
            config_file.save(self.model_dump())
