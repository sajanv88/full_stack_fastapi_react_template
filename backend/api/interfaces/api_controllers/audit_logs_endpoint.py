from typing import Dict, Optional
from fastapi import APIRouter, Depends, status

from api.common.dtos.download_dto import DownloadResponseDto
from api.common.dtos.worker_dto import WorkerPayloadDto
from api.common.exceptions import InvalidOperationException
from api.core.container import get_audit_logs_service
from api.domain.dtos.audit_logs_dto import AuditActionType, AuditLogListDto, DownloadAuditRequestDto
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.audit_logs_service import AuditLogsService
from api.infrastructure.messaging.celery_worker import trigger_download_report


router = APIRouter(prefix="/audit-logs",  dependencies=[
        Depends(check_permissions_for_current_role(
            required_permissions=[
                Permission.AUDIT_LOGS_VIEW_ONLY
                
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

@router.post("/download", status_code=status.HTTP_202_ACCEPTED, response_model=DownloadResponseDto)
async def download_audit_logs(
    download_request: DownloadAuditRequestDto,
    current_user: CurrentUser,
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.AUDIT_LOGS_DOWNLOAD]))
):
    if download_request.total_records <= 0:
        raise InvalidOperationException("Audit log download request must have at least one record.")
    
    payload = WorkerPayloadDto[Dict[str, str | None]](
        data={
            "action": download_request.action if download_request.action else None,
            "requested_by": str(current_user.id)
        },
        label="email-sending",
        tenant_id=str(current_user.tenant_id) if current_user.tenant_id else None
    )

    trigger_download_report.delay(payload.model_dump_json())
    return DownloadResponseDto(message="Download request has been received. You will receive an email once the report is ready.")


