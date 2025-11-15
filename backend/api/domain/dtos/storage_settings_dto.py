from typing import Literal, Optional
from pydantic import BaseModel, Field, field_serializer


class StorageSettingsDto(BaseModel):
    provider: Literal["s3", "azure_blob"]
    is_enabled: bool
    region: str
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None
    aws_bucket_name: Optional[str] = None
    azure_connection_string: Optional[str] = None
    azure_container_name: Optional[str] = None
    updated_by_user_id: Optional[str] = None



class AvailableStorageProviderDto(StorageSettingsDto):
    id: str
    created_at: str
    updated_at: str
    tenant_id: str | None = None

    @field_serializer("aws_secret_key", "aws_access_key", "azure_connection_string")
    def serialize_sensitive_fields(self, value):
        if value is not None:
            return "****"
        return None



