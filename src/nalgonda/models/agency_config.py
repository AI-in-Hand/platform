from pathlib import Path

from agency_swarm import Agent
from pydantic import BaseModel, Field

from nalgonda.agency_config_lock_manager import AgencyConfigLockManager
from nalgonda.constants import CONFIG_FILE_BASE, DEFAULT_CONFIG_FILE
from nalgonda.models.agent_config import AgentConfig


class AgencyConfig(BaseModel):
    """Config for the agency"""

    agency_manifesto: str = Field(default="Agency Manifesto")
    agents: list[AgentConfig]
    agency_chart: list[str | list[str]]  # contains agent roles

    def update_agent_ids_in_config(self, agency_id: str, agents: list[Agent]) -> None:
        """Update the agent IDs in the config file"""
        for agent in agents:
            for agent_conf in self.agents:
                if agent.name == f"{agent_conf.role}_{agency_id}":
                    agent_conf.id = agent.id
                    break

    @classmethod
    def load(cls, agency_id: str) -> "AgencyConfig":
        """Load the config from a file"""
        config_file_name = cls.get_config_name(agency_id)
        config_file_name = config_file_name if config_file_name.exists() else DEFAULT_CONFIG_FILE

        lock = AgencyConfigLockManager.get_lock(agency_id)
        with lock as _, open(config_file_name) as f:
            return cls.model_validate_json(f.read())

    def save(self, agency_id: str) -> None:
        """Save the config to a file"""
        lock = AgencyConfigLockManager.get_lock(agency_id)
        with lock as _, open(self.get_config_name(agency_id), "w") as f:
            f.write(self.model_dump_json(indent=2))

    @staticmethod
    def get_config_name(agency_id: str) -> Path:
        """Get the name of the config file"""
        return Path(f"{CONFIG_FILE_BASE}_{agency_id}.json")
