from typing import Generic, TypeVar

T = TypeVar("T")


class CacheManager(Generic[T]):
    """
    Abstract base class for a cache manager to handle caching operations.
    Specific cache backends should extend this class and implement its methods.
    """

    def get(self, key: str) -> T | None:
        raise NotImplementedError()

    def set(self, key: str, value: T) -> None:
        raise NotImplementedError()

    def delete(self, key: str) -> None:
        raise NotImplementedError()

    def close(self) -> None:
        raise NotImplementedError()
