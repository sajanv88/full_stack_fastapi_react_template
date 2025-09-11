import logging
from fastapi import  Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.db import client, tenant_collection


logger = logging.getLogger(__name__)

class SubdomainTenantDBMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "")
        logger.info(f"Host from header: {host}")
        if not host:
            logger.error("Missing Host header")
            raise HTTPException(status_code=400, detail="Missing Host header")

        # Extract subdomain (tenant1.myapp.com → tenant1)
        parts = host.split(".")
        if len(parts) < 3:  # e.g., myapp.com (no subdomain)
            logger.warning("No subdomain found, hence using default.")
            request.state.db = None
            request.state.tenant_id = None
            return await call_next(request)
            

        tenant = tenant_collection.find_one({"name": parts[0]})

        if not tenant:
            logger.error("Tenant not found")
            raise HTTPException(status_code=404, detail="Tenant not found")

        tenant_id = str(tenant["_id"])

        # Assign tenant-specific DB
        request.state.db = client[f"tenant_{tenant_id}"]
        request.state.tenant_id = tenant_id
        logger.info(f"Using database: tenant_{tenant_id} for the domain {host}")
        response = await call_next(request)
        return response
    