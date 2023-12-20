from abc import ABC, abstractmethod


class AgencyConfigStorageInterface(ABC):
    """Interface for agency config storage"""

    @abstractmethod
    def __enter__(self):
        """Enter context manager"""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""
        pass

    @abstractmethod
    def load(self):
        """Load agency config from the storage"""
        pass

    @abstractmethod
    def save(self, data):
        """Save agency config to the storage"""
        pass
