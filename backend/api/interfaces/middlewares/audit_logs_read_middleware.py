from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from api.common.security import extract_bearer_token
from api.common.utils import capture_audit_log, get_logger
from api.core.container import get_jwt_token_service
from api.domain.dtos.audit_logs_dto import AuditLogDto

logger = get_logger(__name__)

class AuditLogsReadMiddleware(BaseHTTPMiddleware):
    def _get_entity_name(self, path: str) -> str:
        if "/api/v1/users" in path:
            return "User"
        elif "/api/v1/roles" in path:
            return "Role"
        elif "/api/v1/tenants" in path:
            return "Tenant"

        return "Unknown"

    def _is_audited(self, request: Request) -> bool:
        path = request.url.path
        return request.method == "GET" and path.startswith("/api/") and not path.startswith("/api/v1/health")

    async def dispatch(self, request: Request, call_next):
        if self._is_audited(request):
            token = extract_bearer_token(request.headers.get("authorization"))
            payload = await get_jwt_token_service().decode_token(token, type="access_token") if token else None

            entity = self._get_entity_name(request.url.path)
            await capture_audit_log(AuditLogDto(
                action="read",
                entity=entity if entity != "Unknown" else "AuditLog",
                user_id=str(payload.sub) if payload else "Anonymous",
                changes={"info": f"Read access to {request.url.path}"},
                tenant_id=str(payload.tenant_id) if payload and payload.tenant_id else None
            ))

        return await call_next(request)
