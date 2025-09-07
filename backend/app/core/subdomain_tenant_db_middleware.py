from fastapi import  Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.db import client

class SubdomainTenantDBMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "")
        print(f"Host from header: {host}")
        if not host:
            raise HTTPException(status_code=400, detail="Missing Host header")

        # Extract subdomain (tenant1.myapp.com → tenant1)
        parts = host.split(".")
        if len(parts) < 3:  # e.g., myapp.com (no subdomain)
            raise HTTPException(status_code=400, detail="Tenant subdomain missing")

        tenant_id = parts[0]

        # Assign tenant-specific DB
        request.state.db = client[f"tenant_{tenant_id}"]
        print(f"Using database: tenant_{tenant_id} for the domain {host}")
        response = await call_next(request)
        return response