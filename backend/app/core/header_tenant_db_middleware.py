from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import  Request, HTTPException
from app.core.db import client

class TenantDBMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID")
        print(f"Tenant ID from header: {tenant_id}")
        if not tenant_id:
            print("Missing X-Tenant-ID header hence, considering default!")
            request.state.db = None
            return await call_next(request)

        # Select tenant database
        request.state.db = client[f"tenant_{tenant_id}"]
        print(f"Using database: tenant_{tenant_id}")
        response = await call_next(request)
        return response
