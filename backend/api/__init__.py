from fastapi import Depends, FastAPI, APIRouter, Request, status
from contextlib import asynccontextmanager

from fastapi.responses import JSONResponse
from api.common.exceptions import ApiBaseException, ConflictException, NotFoundException, UnauthorizedException
from api.core.container import container
from api.infrastructure.persistence.mongodb import Database
from api.interfaces.middlewares.tenant_middleware import TenantMiddleware, extract_tenant_id_from_headers
from api.interfaces.user_endpoint import router as user_router
from api.interfaces.tenant_endpoint import router as tenant_router
from api.common.logging import configure_logging
from api.core.config import settings
db: Database = container.resolve(Database)

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    # initialization database with application-wide models Typically the host database
    await db.init_db(settings.mongo_db_name, is_tenant=False)
    yield
    # Shutdown code
    await db.close()

app = FastAPI(lifespan=lifespan)
app.add_middleware(TenantMiddleware)

@app.exception_handler(ApiBaseException)
async def api_exception_handler(req: Request, ex: ApiBaseException) -> JSONResponse:
    status_code = status.HTTP_400_BAD_REQUEST
    if isinstance(ex, NotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(ex, ConflictException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(ex, UnauthorizedException):
        status_code = status.HTTP_401_UNAUTHORIZED
    
    return JSONResponse(
        status_code=status_code,
        content={"error": ex.message}
    )
    

router = APIRouter(prefix="/api/v1")

router.include_router(user_router, dependencies=[Depends(extract_tenant_id_from_headers)])
router.include_router(tenant_router)

app.include_router(router)