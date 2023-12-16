import threading
from collections import defaultdict


class AgencyConfigLockManager:
    """Lock manager for agency config files that provides a thread lock for each agency configuration.
    This ensures that each agency configuration can only be accessed or modified by one process at a time.
    """

    # Store locks in a defaultdict where each new key automatically gets a new Lock instance.
    _locks: defaultdict[str, threading.Lock] = defaultdict(threading.Lock)

    @classmethod
    def get_lock(cls, agency_id: str) -> threading.Lock:
        """Retrieve or create a lock for the given agency ID.

        Args:
        agency_id (str): The unique identifier for the agency.

        Returns:
        threading.Lock: The lock object associated with the agency ID.
        """
        return cls._locks[agency_id]
