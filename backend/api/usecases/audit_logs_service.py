from io import BytesIO
from typing import List, Optional

from fastapi import UploadFile
from api.common.audit_logs_repository import AuditLogRepository
from api.common.utils import get_logger
from api.domain.dtos.audit_logs_dto import AuditActionType, AuditLogDto, AuditLogListDto
from api.domain.interfaces.email_service import IEmailService
from api.interfaces.email_templates.download_template_html import download_template

logger = get_logger(__name__)

class AuditLogsService:
    def __init__(self, audit_log_repository: AuditLogRepository, email_service: IEmailService):
        self.audit_log_repository: AuditLogRepository = audit_log_repository
        self.email_service: IEmailService = email_service

    async def read_audit_logs(self, tenant_id: Optional[str] = None, limit: int = 10, skip: int = 0, action: Optional[AuditActionType] = None) -> AuditLogListDto:
        return await self.audit_log_repository.list_audit_logs(tenant_id=tenant_id, limit=limit, skip=skip, action=action)


    async def generate_audit_logs_download(self, action: Optional[AuditActionType] = None, tenant_id: Optional[str] = None) -> List[AuditLogDto]:
        return await self.audit_log_repository.return_all_audit_logs(action=action, tenant_id=tenant_id)

    async def create_audit_log(self, audit_log: AuditLogDto) -> None:
        await self.audit_log_repository.add_audit_log(audit_log)

    async def send_audit_log_report_via_email(self, to_email: str, first_name: str, attachment_data: BytesIO, attachment_filename: str) -> None:
        await self.email_service.send_email(
          to=to_email,
          subject="Audit Logs Report",
          body=download_template(user_first_name=first_name),
          type="html",
          attachments=[UploadFile(file=attachment_data, filename=attachment_filename)]
        )