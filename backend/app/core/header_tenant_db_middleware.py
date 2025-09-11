import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import  Request, HTTPException
from app.core.db import client


logger = logging.getLogger(__name__)

class TenantDBMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID")
        logger.info(f"Tenant ID from header: {tenant_id}")
        if not tenant_id:
            logger.warning("Missing X-Tenant-ID header hence, considering default!")
            request.state.db = None
            request.state.tenant_id = None
            return await call_next(request)

        # Select tenant database
        request.state.db = client[f"tenant_{tenant_id}"]
        request.state.tenant_id = tenant_id
        logger.info(f"Using database: tenant_{tenant_id}")
        response = await call_next(request)
        return response
