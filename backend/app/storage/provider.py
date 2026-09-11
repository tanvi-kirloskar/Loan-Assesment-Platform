import os

from app.storage.base import BaseStorageProvider
from app.storage.local import LocalDiskStorageProvider
from app.storage.s3 import S3StorageProvider


def get_storage_provider() -> BaseStorageProvider:
    """Return the configured document storage provider."""

    storage_provider = os.getenv(
        "STORAGE_PROVIDER",
        "local",
    ).lower()

    if storage_provider == "local":
        return LocalDiskStorageProvider()

    if storage_provider == "s3":
        return S3StorageProvider()

    raise ValueError(
        f"Unsupported STORAGE_PROVIDER: {storage_provider}"
    )