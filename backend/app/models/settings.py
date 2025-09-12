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
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    connection_string: Optional[str] = None

