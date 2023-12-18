import json
from pathlib import Path

from agency_swarm import Agent
from pydantic import BaseModel, Field

from nalgonda.agency_config_lock_manager import AgencyConfigLockManager
from nalgonda.constants import CONFIG_FILE_BASE, DEFAULT_CONFIG_FILE
from nalgonda.models.agent_config import AgentConfig


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
        """Load agency config from file"""
        config_file_path = cls.get_config_path(agency_id)
        if not config_file_path.is_file():
            config_file_path = DEFAULT_CONFIG_FILE

        with AgencyConfigLockManager.get_lock(agency_id), config_file_path.open() as file:
            config = json.load(file)
            config["agency_id"] = agency_id
            return cls.model_validate(config)

    def save(self) -> None:
        with AgencyConfigLockManager.get_lock(self.agency_id), self.get_config_path(self.agency_id).open("w") as file:
            file.write(self.model_dump_json(indent=2))

    @staticmethod
    def get_config_path(agency_id: str) -> Path:
        return CONFIG_FILE_BASE.with_name(f"config_{agency_id}.json")
