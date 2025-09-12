from enum import Enum
from typing import List, Union, Optional
from pydantic import BaseModel

class StorageProvider(str, Enum):
    AWS_S3 = "s3"
    AZURE_BLOB = "azure_blob"


class StorageSettings(BaseModel):
    provider: StorageProvider
    is_enabled: bool
    region: str
    aws_access_key: Optional[str] = None # For AWS S3
    aws_secret_key: Optional[str] = None # For AWS S3
    aws_bucket_name: Optional[str] = None     # For AWS S3
    azure_connection_string: Optional[str] = None # For Azure Blob
    azure_container_name: Optional[str] = None  # For Azure Blob
   

