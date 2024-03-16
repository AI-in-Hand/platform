import logging

from agency_swarm import BaseTool
from pyairtable import Api
from pydantic import Field

from nalgonda.repositories.env_config_firestore_storage import EnvConfigFirestoreStorage
from nalgonda.services.env_config_manager import EnvConfigManager

logger = logging.getLogger(__name__)


class SaveLeadToAirtable(BaseTool):
    """Save a new lead to Airtable."""

    name: str = Field(..., description="Name of the new potential client.")
    email: str = Field(..., description="Email of the new potential client.")
    lead_details: str = Field(..., description="Lead details.")

    def run(self) -> str:
        """Save a new lead to Airtable."""
        logger.info(f"Saving new lead to Airtable: {self.name}, {self.email}, {self.lead_details}")
        env_config_storage = EnvConfigFirestoreStorage()
        env_config_manager = EnvConfigManager(env_config_storage)

        try:
            airtable_base_id = env_config_manager.get_by_key("AIRTABLE_BASE_ID")
            airtable_table_id = env_config_manager.get_by_key("AIRTABLE_TABLE_ID")
            airtable_token = env_config_manager.get_by_key("AIRTABLE_TOKEN")

            api = Api(airtable_token)
            table = api.table(airtable_base_id, airtable_table_id)

            data = {
                "Name": self.name,
                "Email": self.email,
                "Lead Details": self.lead_details,
            }

            response = table.create(data)
            airtable_message = f"Response from Airtable: id: {response['id']}, createdTime: {response['createdTime']}"
        except Exception as e:
            airtable_message = f"Error while saving lead to Airtable: {e}"
            logger.exception(airtable_message)

        logger.info(airtable_message)

        return airtable_message
