from fastapi import APIRouter, Depends, status

from api.core.container import get_audit_logs_service
from api.domain.dtos.audit_logs_dto import AuditLogListDto
from api.domain.enum.permission import Permission
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.audit_logs_service import AuditLogsService


# router = APIRouter(prefix="/audit-logs",  dependencies=[
#         Depends(check_permissions_for_current_role(
#             required_permissions=[
#                 Permission.AUDIT_LOGS_VIEW_ONLY,
#                 Permission.AUDIT_LOGS_DOWNLOAD
#             ]
#         )
#     )]
#    )
router = APIRouter(prefix="/audit-logs")

router.tags = ["Audit Logs"]


@router.get("/", response_model=AuditLogListDto, status_code=status.HTTP_200_OK)
async def list_audit_logs(
    limit: int = 10,
    skip: int = 0,
    log_service: AuditLogsService = Depends(get_audit_logs_service)
):
    return await log_service.read_audit_logs(limit=limit, skip=skip)

@router.get("/download", status_code=status.HTTP_200_OK)
async def download_audit_logs():
    return None


