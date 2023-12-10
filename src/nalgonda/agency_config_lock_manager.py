import threading
from collections import defaultdict

class AgencyConfigLockManager:
    """Lock manager for agency config files"""

    _locks: dict[str, threading.Lock] = defaultdict(threading.Lock)

    @classmethod
    def get_lock(cls, agency_id):
        return cls._locks[agency_id]
