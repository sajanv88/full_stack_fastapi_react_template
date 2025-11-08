import glob
import json
from typing import List, Optional
from api.common.audit_logs_repository import AuditLogRepository
from api.common.utils import get_logger
from api.domain.dtos.audit_logs_dto import AuditActionType, AuditLogDto, AuditLogListDto
from collections import deque

logger = get_logger(__name__)

class AuditLogsService:
    def __init__(self, audit_log_repository: AuditLogRepository):
        self.audit_log_repository: AuditLogRepository = audit_log_repository

    async def read_audit_logs(self, tenant_id: Optional[str] = None, limit: int = 10, skip: int = 0, action: Optional[AuditActionType] = None) -> AuditLogListDto:
        return await self.audit_log_repository.list_audit_logs(tenant_id=tenant_id, limit=limit, skip=skip, action=action)


    async def generate_audit_logs_download(self) -> None:
        # Placeholder implementation
        return None
    
    async def create_audit_log(self, audit_log: AuditLogDto) -> None:
        await self.audit_log_repository.add_audit_log(audit_log)