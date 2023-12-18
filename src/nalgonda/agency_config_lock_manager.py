import threading
from collections import defaultdict


class AgencyConfigLockManager:
    """Manages locking for agency configuration files.

    This manager guarantees that each agency configuration has a unique lock,
    preventing simultaneous access and modification by multiple processes.
    """

    # Mapping from agency ID to its corresponding Lock.
    _locks: "defaultdict[str, threading.Lock]" = defaultdict(threading.Lock)

    @classmethod
    def get_lock(cls, agency_id: str) -> threading.Lock:
        """Retrieves the lock for a given agency ID, creating it if not present.

        Args:
            agency_id (str): The unique identifier for the agency.

        Returns:
            threading.Lock: The lock associated with the agency ID.
        """
        return cls._locks[agency_id]
