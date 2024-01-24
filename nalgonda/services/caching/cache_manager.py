from typing import Generic, TypeVar

T = TypeVar("T")


class CacheManager(Generic[T]):
    """
    Abstract base class for a cache manager to handle caching operations.
    Specific cache backends should extend this class and implement its methods.
    """

    async def get(self, key: str) -> T | None:
        raise NotImplementedError()

    async def set(self, key: str, value: T) -> None:
        raise NotImplementedError()

    async def delete(self, key: str) -> None:
        raise NotImplementedError()

    async def close(self) -> None:
        raise NotImplementedError()
