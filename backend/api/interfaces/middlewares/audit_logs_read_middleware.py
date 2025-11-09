from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from api.common.utils import capture_audit_log, get_logger
from api.core.container import get_jwt_token_service, get_role_service, get_subscription_plan_service, get_user_service
from api.domain.dtos.audit_logs_dto import AuditLogDto
from api.infrastructure.security.current_user import current_user_optional

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
    async def dispatch(self, request: Request, call_next):
        token = None
        if "authorization" in request.headers:
            token = request.headers["authorization"].replace("Bearer ", "")
        user_service = get_user_service()
        jwt_service = get_jwt_token_service()
        role_service = get_role_service()
        subscription_service = get_subscription_plan_service()    
        if request.method == "GET":
            current_user = await current_user_optional(
                token,
                user_service=user_service,
                token_service=jwt_service,
                role_service=role_service,
                subscription_service=subscription_service
            )
        
            entity = self._get_entity_name(request.url.path)
            await capture_audit_log(AuditLogDto(
                action="read",
                entity=entity if entity != "Unknown" else "AuditLog",
                user_id=str(current_user.id) if current_user else "Anonymous",
                changes={"info": f"Read access to {request.url.path}"},
                tenant_id=str(current_user.tenant_id) if current_user and current_user.tenant_id else None
            ))
    
        
        return await call_next(request)
        