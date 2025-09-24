from typing import Literal, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class WorkerPayloadDto(BaseModel, Generic[T]):
    label: Literal["post-tenant-creation", "email-sending", "post-delete-cleanup", "post-tenant-deletion"] = "email-sending"
    data: T | None = None
    tenant_id: str | None = None
    
