from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel
from datetime import datetime


class AuditLogDto(BaseModel):
    entity: str
    action: Literal["create", "update", "delete", "read", "login", "logout"]
    changes: Dict[str, Any] = {}
    user_id: str
    timestamp: str = datetime.now().isoformat()
    tenant_id: Optional[str] = None

class AuditLogListDto(BaseModel):
    total: int
    logs: list[AuditLogDto]
    has_next: bool
    has_previous: bool
    limit: int
    skip: int
