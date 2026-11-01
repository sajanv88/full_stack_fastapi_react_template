from typing import Annotated, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import  Depends, Request, status
from fastapi.responses import JSONResponse
from beanie import PydanticObjectId
from api.common.exceptions import error_body
from api.common.tenant_context import reset_active_database
from api.common.utils import get_host_main_domain_name, get_logger, is_subdomain
from api.core.config import settings

from api.core.container import get_tenant_service
from api.core.exceptions import TenantNotFoundException
from api.domain.entities.tenant import Tenant
from api.infrastructure.persistence.mongodb import mongo_client as db

logger = get_logger(__name__)

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only the API touches tenant data, static files and the SPA shell don't need a tenant.
        if not request.url.path.startswith("/api/"):
            request.state.tenant_id = None
            return await call_next(request)

        tenant_id: Optional[str] = None
        tenant_host = get_tenant_host(request)
        logger.debug(f"Tenant host found: {tenant_host}")
        tenant_service = get_tenant_service()

        if tenant_host:
            try:
                tenant: Tenant
                if is_subdomain(tenant_host):
                    logger.debug(f"Host '{tenant_host}' identified as subdomain.")
                    tenant = await tenant_service.find_by_subdomain(tenant_host)
                else:
                    logger.debug(f"Host '{tenant_host}' identified as custom domain.")
                    tenant = await tenant_service.find_by_custom_domain(tenant_host)
                
                tenant_id = str(tenant.id)
                logger.debug(f"Tenant ID resolved from custom domain '{tenant_host}': {tenant_id}")
                request.state.frontend_host = tenant_host
            except TenantNotFoundException as e:
                logger.warning(f"Error resolving tenant from custom domain '{tenant_host}': {e}")
                
        
        if tenant_id is None:
            requested_tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get('tenant_id') or None
            if requested_tenant_id is not None:
                if not PydanticObjectId.is_valid(requested_tenant_id):
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content=error_body("Invalid tenant ID.", status.HTTP_400_BAD_REQUEST),
                    )
                # Never open a database for an unknown tenant, any caller can send this header.
                try:
                    await tenant_service.get_tenant_by_id(requested_tenant_id)
                except TenantNotFoundException as e:
                    return JSONResponse(
                        status_code=status.HTTP_404_NOT_FOUND,
                        content=error_body(e.message, status.HTTP_404_NOT_FOUND),
                    )
                tenant_id = requested_tenant_id

        if tenant_id is not None:
            logger.debug(f"Tenant ID found: {tenant_id}")
            request.state.tenant_id = PydanticObjectId(tenant_id)
            token = await db.use_database(f"tenant_{tenant_id}", is_tenant=True)
        else:
            logger.debug("No tenant ID provided, using default database.")
            request.state.tenant_id = None
            token = await db.use_database(settings.mongo_db_name, is_tenant=False)

        try:
            return await call_next(request)
        finally:
            reset_active_database(token)



def get_tenant_host(request: Request) -> Optional[str]:
    """
    Extracts the tenant-specific host (subdomain) from the incoming request.
    Returns None if the host matches the main domain.
    """
    # Try HTTP/2 ':authority' → fall back to 'host' → finally use parsed URL
    host = (
        request.headers.get(":authority")
        or request.headers.get("host")
        or request.url.hostname
    )
    if not host:
        return None

    host = host.split(':')[0].lower()  # Remove port if present and convert to lowercase

    # Compare against main domain
    main_domain = get_host_main_domain_name().lower()
    if host == main_domain:
        # If the host is exactly the main domain, return None (no tenant)
        return None

    if host.startswith("localhost") or host.startswith("127.0.0.1"):
        # Handle localhost with optional
        return None
    
    logger.debug(f"Extracted host: {host}")
    return host

def get_tenant_id(request: Request) -> PydanticObjectId | None:
    return getattr(request.state, "tenant_id", None)

def frontend_dynamic_host(request: Request) -> str:
   return getattr(request.state, "frontend_host", get_host_main_domain_name())


FrontendHost = Annotated[str, Depends(frontend_dynamic_host)]