from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, field_serializer, Field


class StorageSettingsDTO(BaseModel):
    provider: Literal["s3", "azure_blob"]
    is_enabled: bool
    region: str
    aws_access_key: Optional[str] | None = Field(None, exclude=False)  # For AWS S3
    aws_secret_key: Optional[str] | None = Field(None, exclude=False)  # For AWS S3
    aws_bucket_name: Optional[str] | None = Field(None, exclude=False)  # For AWS S3
    azure_connection_string: Optional[str] | None = Field(None, exclude=False)  # For Azure Blob
    azure_container_name: Optional[str] | None = Field(None, exclude=False)  # For Azure Blob


class AvailableStorageProviderDTO(StorageSettingsDTO):
    id: str
    created_at: str
    updated_at: str
    tenant_id: str | None = None

    

    


