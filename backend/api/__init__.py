from fastapi import FastAPI, APIRouter, Request, status
from contextlib import asynccontextmanager

from fastapi.responses import JSONResponse
from api.common.exceptions import ApiBaseException, ConflictException, InvalidOperationException, NotFoundException, UnauthorizedException
from api.common.utils import get_logger, is_tenancy_enabled
from api.core.container import container
from api.core.exceptions import InvalidSubdomainException, TenantNotFoundException
from api.infrastructure.persistence.mongodb import Database
from api.interfaces.middlewares.known_domain_middleware import KnownDomainMiddleware
from api.interfaces.middlewares.tenant_middleware import TenantMiddleware
from api.interfaces.api_controllers.account_endpoint import router as account_router
from api.interfaces.api_controllers.user_endpoint import router as user_router
from api.interfaces.api_controllers.tenant_endpoint import router as tenant_router
from api.interfaces.api_controllers.role_endpoint import router as role_router
from api.interfaces.api_controllers.app_configuration_endpoint import router as app_configuration_router
from api.interfaces.api_controllers.storage_endpoint import router as storage_router
from api.interfaces.api_controllers.permissions_endpoint import router as permissions_router
from api.common.logging import configure_logging
from api.core.config import settings

db: Database = container.resolve(Database)

logger = get_logger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    # initialization database with application-wide models Typically the host database
    await db.init_db(settings.mongo_db_name, is_tenant=False)
    yield
    # Shutdown code
    await db.close()

app = FastAPI(lifespan=lifespan)

@app.exception_handler(ApiBaseException)
async def api_exception_handler(req: Request, ex: ApiBaseException) -> JSONResponse:
    status_code = status.HTTP_400_BAD_REQUEST
    if isinstance(ex, NotFoundException) or isinstance(ex, TenantNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(ex, ConflictException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(ex, UnauthorizedException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(ex, InvalidSubdomainException):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(ex, InvalidOperationException):
        status_code = status.HTTP_406_NOT_ACCEPTABLE

    
    logger.error(f"API Exception: {ex.message}")
    return JSONResponse(
        status_code=status_code,
        content={"error": ex.message, "code": status_code}
    )
    
app.add_middleware(KnownDomainMiddleware)

if is_tenancy_enabled():
    app.add_middleware(TenantMiddleware)
    logger.info("Multi-tenancy is enabled.")


router = APIRouter(prefix="/api/v1")

if is_tenancy_enabled():
    router.include_router(tenant_router)

router.include_router(app_configuration_router)
router.include_router(account_router)
router.include_router(user_router)
router.include_router(role_router)
router.include_router(permissions_router)
router.include_router(storage_router)





app.include_router(router)
