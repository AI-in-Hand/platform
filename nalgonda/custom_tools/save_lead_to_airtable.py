import logging

from agency_swarm import BaseTool
from pyairtable import Api
from pydantic import Field

from nalgonda.settings import settings

logger = logging.getLogger(__name__)


class SaveLeadToAirtable(BaseTool):
    """Save a new lead to Airtable."""

    name: str = Field(..., description="Name of the new potential client.")
    email: str = Field(..., description="Email of the new potential client.")
    lead_details: str = Field(..., description="Lead details.")

    def run(self) -> str:
        """Save a new lead to Airtable."""
        logger.info(f"Saving new lead to Airtable: {self.name}, {self.email}, {self.lead_details}")

        try:
            api = Api(settings.airtable_token)
            table = api.table(settings.airtable_base_id, settings.airtable_table_id)

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
