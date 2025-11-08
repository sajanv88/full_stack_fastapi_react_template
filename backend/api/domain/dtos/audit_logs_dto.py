from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel
from datetime import datetime

AuditActionType = Literal["create", "update", "delete", "read", "login", "logout", "error"]
class AuditLogDto(BaseModel):
    entity: str
    action: AuditActionType
    changes: Dict[str, Any] = {}
    user_id: Optional[str] = None
    timestamp: str = datetime.now().isoformat()
    tenant_id: Optional[str] = None

class AuditLogListDto(BaseModel):
    total: int
    logs: list[AuditLogDto]
    has_next: bool
    has_previous: bool
    limit: int
    skip: int
