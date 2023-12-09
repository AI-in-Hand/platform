import threading


class AgencyConfigLockManager:
    """Lock manager for agency config files"""

    _locks: dict[str, threading.Lock] = {}

    @classmethod
    def get_lock(cls, agency_id):
        if agency_id not in cls._locks:
            cls._locks[agency_id] = threading.Lock()
        return cls._locks[agency_id]
