from typing import Optional
from fastapi import APIRouter, Depends, status

from api.core.container import get_audit_logs_service
from api.domain.dtos.audit_logs_dto import AuditActionType, AuditLogListDto
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.audit_logs_service import AuditLogsService


router = APIRouter(prefix="/audit-logs",  dependencies=[
        Depends(check_permissions_for_current_role(
            required_permissions=[
                Permission.AUDIT_LOGS_VIEW_ONLY,
                Permission.AUDIT_LOGS_DOWNLOAD
            ]
        )
    )]
   )


router.tags = ["Audit Logs"]


@router.get("/", response_model=AuditLogListDto, status_code=status.HTTP_200_OK)
async def list_audit_logs(
    current_user: CurrentUser,
    limit: int = 10,
    skip: int = 0,
    action: Optional[AuditActionType] = None,
    log_service: AuditLogsService = Depends(get_audit_logs_service)
):
    tenant_id = str(current_user.tenant_id) if current_user.tenant_id else None
    return await log_service.read_audit_logs(tenant_id=tenant_id, limit=limit, skip=skip, action=action)

@router.get("/download", status_code=status.HTTP_200_OK)
async def download_audit_logs():
    return None


