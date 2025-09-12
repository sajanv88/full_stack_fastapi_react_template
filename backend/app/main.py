import os
import logging
from fastapi import FastAPI, APIRouter, HTTPException, Request, Security
from fastapi.exception_handlers import http_exception_handler
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse
from fastapi.security.api_key import APIKeyHeader
from app.api.routes import  users
from app.core.db import ensure_indexes
from app.core.seeder import seed_default_data
from app.api.routes import auth, role, dashboard, permissions, ai, tenant, configuration, storage_setting
from app.core.subdomain_tenant_db_middleware import SubdomainTenantDBMiddleware
from app.core.header_tenant_db_middleware import TenantDBMiddleware
from app.core.utils import is_tenancy_enabled
from app.loggin_conf import configure_logging




logger = logging.getLogger(__name__)

multi_tenancy_strategy = os.getenv("MULTI_TENANCY_STRATEGY", "none").lower()
api_key_header = APIKeyHeader(name="x-tenant-id", auto_error=False)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "myapp")



build_path = os.path.join(os.path.dirname(__file__), "ui")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    configure_logging()
    logger.info("Starting application...")
    await ensure_indexes()
    logger.info("Database indexes created successfully")
    await seed_default_data()
    logger.info("Default data seeded successfully")
    yield
    # Shutdown
    logger.info("Application shutting down")

app = FastAPI(
    lifespan=lifespan,
    title="FastAPI React & MongoDb Template",
    description="A template for building full-stack applications with FastAPI, React and MongoDB. Optional multi-tenancy support.",
    version="1.0.0"
)

@app.exception_handler(HTTPException)
async def http_exception_handler_logging(request: Request, exc: HTTPException):
    logger.error(f"HTTP error occurred: {exc.status_code} - {exc.detail}")
    return await http_exception_handler(request, exc)


if multi_tenancy_strategy == "subdomain":
    logger.info("Using subdomain multi-tenancy")
    app.add_middleware(SubdomainTenantDBMiddleware)
elif multi_tenancy_strategy == "header":
    logger.info("Using header multi-tenancy")
    app.add_middleware(TenantDBMiddleware)


# Mount static files only if they exist (for production Docker deployment)
if os.path.exists(build_path) and os.path.exists(os.path.join(build_path, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(build_path, "assets")), name="assets")
    logger.info("Static files mounted successfully")
else:
    logger.warning("Static files directory not found - running in development mode")

@app.get("/", include_in_schema=False)
async def serve_react_app():
    try:
        if os.path.exists(os.path.join(build_path, "index.html")):
            return FileResponse(os.path.join(build_path, "index.html"))
        else:
            return {"message": "FastAPI backend is running", "mode": "development", "docs": "/docs"}
    except Exception as e:
        logger.error(f"Error serving React app: {e}")
        return {"message": "FastAPI backend is running", "mode": "development", "docs": "/docs"}



router_v1 = APIRouter(prefix="/api/v1")

# Only enable tenant endpoint when multi-tenancy is enabled
if is_tenancy_enabled():
    router_v1 = APIRouter(prefix="/api/v1", dependencies=[Security(api_key_header)])

router_v1.include_router(tenant.router)
router_v1.include_router(users.router)
router_v1.include_router(auth.router)
router_v1.include_router(role.router)
router_v1.include_router(dashboard.router)
router_v1.include_router(permissions.router)
router_v1.include_router(storage_setting.router)
router_v1.include_router(ai.router)
router_v1.include_router(configuration.router)



app.include_router(router_v1)

# Catch-all route for React Router (only in production with static files)
@app.get("/{full_path:path}", include_in_schema=False)
async def react_router(full_path: str):
    if os.path.exists(os.path.join(build_path, "index.html")):
        return FileResponse(os.path.join(build_path, "index.html"))
    else:
        return {"message": "API endpoint not found", "available_docs": "/docs", "api_base": "/api/v1"}

