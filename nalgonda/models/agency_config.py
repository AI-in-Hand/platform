from agency_swarm import Agent
from pydantic import BaseModel, Field

from nalgonda.models.agent_config import AgentConfig
from nalgonda.persistence.agency_config_firestore_storage import AgencyConfigFirestoreStorage


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
        with AgencyConfigFirestoreStorage(agency_id) as config_document:
            config = config_document.load()

        config["agency_id"] = agency_id
        return cls.model_validate(config)

    def save(self) -> None:
        with AgencyConfigFirestoreStorage(self.agency_id) as config_document:
            config_document.save(self.model_dump())
