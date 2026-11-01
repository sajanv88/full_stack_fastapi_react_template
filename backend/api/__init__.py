import os
from bson.errors import InvalidId
from fastapi import FastAPI, APIRouter, Request, status
from contextlib import asynccontextmanager

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
import stripe
from api.common.exceptions import (
    ApiBaseException,
    AuthenticationFailedException,
    ConflictException,
    ForbiddenException,
    InvalidOperationException,
    NotFoundException,
    TooManyRequestsException,
    UnauthorizedException,
    error_body,
)
from api.common.utils import get_logger, is_tenancy_enabled
from api.core.container import container
from api.core.exceptions import InvalidSubdomainException, TenantNotFoundException
from api.infrastructure.persistence.mongodb import Database
from api.interfaces.middlewares.audit_logs_read_middleware import AuditLogsReadMiddleware
from api.interfaces.middlewares.redis_cache_middleware import RedisCacheMiddleware
from api.interfaces.middlewares.security_headers_middleware import SecurityHeadersMiddleware
from api.interfaces.middlewares.tenant_middleware import TenantMiddleware
from api.interfaces.api_controllers.account_endpoint import router as account_router
from api.interfaces.api_controllers.user_endpoint import router as user_router
from api.interfaces.api_controllers.tenant_endpoint import router as tenant_router
from api.interfaces.api_controllers.role_endpoint import router as role_router
from api.interfaces.api_controllers.app_configuration_endpoint import router as app_configuration_router
from api.interfaces.api_controllers.storage_endpoint import router as storage_router
from api.interfaces.api_controllers.permissions_endpoint import router as permissions_router
from api.interfaces.api_controllers.dashboard_endpoint import router as dashboard_router
from api.interfaces.api_controllers.ai_endpoint import router as ai_router
from api.interfaces.api_controllers.health_endpoint import router as health_router
from api.interfaces.api_controllers.manage_security_endpoint import router as manage_security_router
from api.interfaces.api_controllers.features_endpoint import router as features_router
from api.interfaces.api_controllers.product_endpoint import router as product_router
from api.interfaces.api_controllers.prices_endpoint import router as prices_router
from api.interfaces.api_controllers.billing_endpoint import router as billing_router
from api.interfaces.api_controllers.stripe_endpoint import router as stripe_router, webhook_router as stripe_webhook_router
from api.interfaces.api_controllers.invoice_endpoint import router as invoice_router
from api.interfaces.api_controllers.checkout_endpoint import router as checkout_router
from api.interfaces.api_controllers.notification_endpoint import router as notification_router
from api.interfaces.api_controllers.audit_logs_endpoint import router as audit_logs_router
from api.interfaces.api_controllers.sso_settings_endpoint import router as sso_router
from api.interfaces.api_controllers.branding_endpoint import router as branding_router

from api.common.logging import configure_logging
from api.core.config import settings
from api.infrastructure.persistence.seeder import seed_initial_data

build_path = os.path.join(os.path.dirname(__file__), "ui")


db: Database = container.resolve(Database)

logger = get_logger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    # initialization database with application-wide models Typically the host database
    await db.init_db(settings.mongo_db_name, is_tenant=False)
    await seed_initial_data()
    yield
    # Shutdown code
    await db.close()

app = FastAPI(
    lifespan=lifespan, 
    title="FastAPI React & MongoDb Template",
    description="A template for building full-stack applications with FastAPI, React and MongoDB. Optional multi-tenancy support.",
    version="1.0.0"
)



@app.exception_handler(ApiBaseException)
async def api_exception_handler(req: Request, ex: ApiBaseException) -> JSONResponse:
    status_code = status.HTTP_400_BAD_REQUEST
    if isinstance(ex, NotFoundException) or isinstance(ex, TenantNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(ex, ConflictException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(ex, (UnauthorizedException, AuthenticationFailedException)):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(ex, ForbiddenException):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(ex, TooManyRequestsException):
        status_code = status.HTTP_429_TOO_MANY_REQUESTS
    elif isinstance(ex, InvalidSubdomainException):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(ex, InvalidOperationException):
        status_code = status.HTTP_406_NOT_ACCEPTABLE


    logger.error(f"API Exception: {ex.message}")
    return JSONResponse(
        status_code=status_code,
        content=error_body(ex.message, status_code)
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(req: Request, ex: RequestValidationError) -> JSONResponse:
    errors = jsonable_encoder(ex.errors())
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    return JSONResponse(
        status_code=status_code,
        content={**error_body(errors[0]["msg"] if errors else "Invalid request.", status_code), "detail": errors}
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(req: Request, ex: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=ex.status_code,
        content=error_body(str(ex.detail), ex.status_code),
        headers=ex.headers
    )


@app.exception_handler(InvalidId)
async def invalid_id_exception_handler(req: Request, ex: InvalidId) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_body("The given identifier is not valid.", status.HTTP_400_BAD_REQUEST)
    )


@app.exception_handler(stripe.StripeError)
async def stripe_exception_handler(req: Request, ex: stripe.StripeError) -> JSONResponse:
    logger.error(f"Stripe error: {ex}")
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content=error_body(ex.user_message or "The payment provider request failed.", status.HTTP_502_BAD_GATEWAY)
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(req: Request, ex: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception on {req.method} {req.url.path}", exc_info=ex)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_body("Internal server error.", status.HTTP_500_INTERNAL_SERVER_ERROR)
    )


app.add_middleware(AuditLogsReadMiddleware)
app.add_middleware(RedisCacheMiddleware)

if is_tenancy_enabled():
    app.add_middleware(TenantMiddleware)
    logger.info("Multi-tenancy is enabled.")

app.add_middleware(SecurityHeadersMiddleware)


# Mount static files only if they exist (for production Docker deployment)
if os.path.exists(build_path) and os.path.exists(os.path.join(build_path, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(build_path, "assets")), name="assets")
    logger.info("Static files mounted successfully")
else:
    logger.warning(f"Static files directory not found - running in {settings.fastapi_env} mode")




router = APIRouter(prefix="/api/v1")


router.include_router(health_router)

if is_tenancy_enabled():
    router.include_router(tenant_router)
    router.include_router(features_router)
    router.include_router(branding_router)



router.include_router(app_configuration_router)
router.include_router(account_router)
router.include_router(manage_security_router)
router.include_router(dashboard_router)

router.include_router(user_router)
router.include_router(role_router)
router.include_router(permissions_router)
router.include_router(storage_router)
router.include_router(ai_router)
router.include_router(product_router)
router.include_router(prices_router)
router.include_router(billing_router)
router.include_router(stripe_router)
router.include_router(stripe_webhook_router)
router.include_router(invoice_router)
router.include_router(checkout_router)
router.include_router(notification_router)
router.include_router(audit_logs_router)
router.include_router(sso_router)


app.include_router(router)



# Catch-all route for React Router (only in production with static files)
@app.get("/{full_path:path}", include_in_schema=False)
async def react_router(full_path: str):
    # An unknown API route has to stay an API error, never the HTML of the SPA.
    if full_path.startswith("api/"):
        raise StarletteHTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API endpoint not found.")

    if os.path.exists(os.path.join(build_path, "index.html")):
        return FileResponse(os.path.join(build_path, "index.html"))
    else:
        return {"message": "API endpoint not found", "available_docs": "/docs", "api_base": "/api/v1"}

