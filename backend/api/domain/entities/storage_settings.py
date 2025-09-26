
from enum import Enum

from typing import  Optional
from api.domain.dtos.storage_settings_dto import AvailableStorageProviderDTO
from api.domain.entities.api_base_model import ApiBaseModel

class StorageProvider(str, Enum):
    AWS_S3 = "s3"
    AZURE_BLOB = "azure_blob"


class StorageSettings(ApiBaseModel):
    provider: StorageProvider
    is_enabled: bool
    region: str
    aws_access_key: Optional[str] = None # For AWS S3
    aws_secret_key: Optional[str] = None # For AWS S3
    aws_bucket_name: Optional[str] = None     # For AWS S3
    azure_connection_string: Optional[str] = None # For Azure Blob
    azure_container_name: Optional[str] = None  # For Azure Blob

    async def to_serializable_dict(self) -> AvailableStorageProviderDTO:
        base_doc = await super().to_serializable_dict()
        result = {
            **base_doc,
            "provider": self.provider.value,
            "is_enabled": self.is_enabled,
            "region": self.region,
            "aws_access_key": self.aws_access_key if self.aws_access_key else None,
            "aws_secret_key": self.aws_secret_key if self.aws_secret_key else None,
            "aws_bucket_name": self.aws_bucket_name if self.aws_bucket_name else None,
            "azure_connection_string": self.azure_connection_string if self.azure_connection_string else None,
            "azure_container_name": self.azure_container_name if self.azure_container_name else None
        }
        return AvailableStorageProviderDTO(**result)

    class Settings:
        name = "settings"


