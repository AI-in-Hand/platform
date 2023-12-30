import json
from typing import Any, Optional

from agency_swarm import Agent
from pydantic import BaseModel, Field

from nalgonda.constants import DEFAULT_CONFIG_FILE
from nalgonda.models.agent_config import AgentConfig
from nalgonda.persistence.agency_config_firestore_storage import AgencyConfigFirestoreStorage


class AgencyConfig(BaseModel):
    """Agency configuration model"""

    agency_id: str = Field(...)
    agency_manifesto: str = Field(default="Agency Manifesto")
    agents: list[AgentConfig] = Field(...)
    agency_chart: list[str | list[str]] = Field(...)  # contains agent roles

    @classmethod
    def load(cls, agency_id: str) -> Optional["AgencyConfig"]:
        with AgencyConfigFirestoreStorage(agency_id) as config_document:
            config_data = config_document.load()
        return cls.model_validate(config_data) if config_data else None

    @classmethod
    def load_or_create(cls, agency_id: str) -> "AgencyConfig":
        with AgencyConfigFirestoreStorage(agency_id) as config_document:
            config_data = config_document.load()

        if not config_data:
            config_data = cls._create_default_config()

        config_data["agency_id"] = agency_id
        model = cls.model_validate(config_data)

        with AgencyConfigFirestoreStorage(agency_id) as config_document:
            config_document.save(config_data)

        return model

    def update(self, update_data: dict[str, Any]) -> None:
        for key, value in update_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def save(self) -> None:
        with AgencyConfigFirestoreStorage(self.agency_id) as config_document:
            config_document.save(self.model_dump())

    def update_agent_ids_in_config(self, agents: list[Agent]) -> None:
        """Update agent ids in config with the ids of the agents in the swarm"""
        for agent in agents:
            for agent_config in self.agents:
                if agent.name == f"{agent_config.role}_{self.agency_id}":
                    agent_config.id = agent.id

    @classmethod
    def _create_default_config(cls) -> dict[str, Any]:
        """Creates a default config for the agency."""
        with DEFAULT_CONFIG_FILE.open() as file:
            config = json.load(file)
        return config
