import logging
import os
from collections import defaultdict

logger = logging.getLogger(__name__)


class EnvConfigFirestoreStorage:
    def __init__(self):
        # Storing environment configurations
        # TODO: interface with Firestore, add encryption
        self.configs = defaultdict(lambda: {"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY_TEST")})

    def get_config(self, owner_id: str) -> dict:
        # Placeholder for fetching environment config based on owner_id
        # TODO: adapt to fetch from Firestore, decrypt
        logger.info(f"Fetching environment config for owner_id: {owner_id}")
        return self.configs[owner_id]
