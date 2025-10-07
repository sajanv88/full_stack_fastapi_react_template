from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import  Request
from beanie import PydanticObjectId
from api.common.utils import get_logger
from api.core.config import settings

from api.infrastructure.persistence.mongodb import mongo_client as db

logger = get_logger(__name__)

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):       
        tenant_id = request.headers.get("X-Tenant-ID") or request.query_params.get('tenant_id') or None
        logger.debug(f"Tenant ID found: {tenant_id}")
 
        if tenant_id is not None:
            request.state.tenant_id = PydanticObjectId(tenant_id)
            # Initialize the database for the tenant and initialize Beanie with tenant-specific models
            await db.init_db(f"tenant_{tenant_id}", is_tenant=True)
            logger.debug(f"Database initialized for tenant: tenant_{tenant_id}")
        else:
            # If no tenant ID is provided, ensure we are using the default database
            if db.is_tenant_active():
                # Reset to default DB if no tenant ID is provided
                await db.init_db(settings.mongo_db_name, is_tenant=False)
            request.state.tenant_id = None
            logger.debug("No tenant ID provided, using default database.")

        response = await call_next(request)
        return response


async def get_tenant_id(request: Request) -> PydanticObjectId | None:
    return getattr(request.state, "tenant_id", None)


