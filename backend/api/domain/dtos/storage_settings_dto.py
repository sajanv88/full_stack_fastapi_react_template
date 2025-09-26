from typing import Literal
from pydantic import BaseModel


class StorageSettingsDTO(BaseModel):
    provider: Literal["s3", "azure_blob"]
    is_enabled: bool
    region: str
    aws_access_key: str | None = None  # For AWS S3
    aws_secret_key: str | None = None  # For AWS S3
    aws_bucket_name: str | None = None  # For AWS S3
    azure_connection_string: str | None = None  # For Azure Blob
    azure_container_name: str | None = None  # For Azure Blob


class AvailableStorageProviderDTO(StorageSettingsDTO):
    id: str
    created_at: str
    updated_at: str
    tenant_id: str | None = None


