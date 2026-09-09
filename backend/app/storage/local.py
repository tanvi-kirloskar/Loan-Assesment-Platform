from pathlib import Path

from app.storage.base import BaseStorageProvider


class LocalDiskStorageProvider(BaseStorageProvider):
    """Store document files on the local filesystem."""

    def __init__(self, base_directory: str = "storage"):
        self.base_directory = Path(base_directory)

    def store(
        self,
        file_data: bytes,
        storage_key: str,
    ) -> str:
        destination = self.base_directory / storage_key

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination.write_bytes(file_data)

        return storage_key

    def delete(
        self,
        storage_key: str,
    ) -> None:
        destination = self.base_directory / storage_key

        if destination.exists():
            destination.unlink()
