import os

import boto3

from app.storage.base import BaseStorageProvider


class S3StorageProvider(BaseStorageProvider):
    """Store document files in Amazon S3."""

    def __init__(
        self,
        bucket_name: str | None = None,
        region_name: str | None = None,
    ):
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME")
        self.region_name = region_name or os.getenv("AWS_REGION")

        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME is not configured.")

        self.client = boto3.client(
            "s3",
            region_name=self.region_name,
        )

    def store(
        self,
        file_data: bytes,
        storage_key: str,
    ) -> str:
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=storage_key,
            Body=file_data,
        )

        return storage_key

    def delete(
        self,
        storage_key: str,
    ) -> None:
        self.client.delete_object(
            Bucket=self.bucket_name,
            Key=storage_key,
        )