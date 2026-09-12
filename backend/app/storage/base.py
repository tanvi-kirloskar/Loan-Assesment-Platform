from abc import ABC, abstractmethod


class BaseStorageProvider(ABC):
    """Abstract interface for document storage backends."""

    @abstractmethod
    def store(
        self,
        file_data: bytes,
        storage_key: str,
    ) -> str:
        """Store file bytes and return the storage key."""
        raise NotImplementedError

    @abstractmethod
    def retrieve(
        self,
        storage_key: str,
    ) -> bytes:
        """Retrieve file bytes by storage key."""
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        storage_key: str,
    ) -> None:
        """Delete a stored file by its storage key."""
        raise NotImplementedError