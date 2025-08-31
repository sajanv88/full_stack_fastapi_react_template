from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager

from app.api.routes import settings, users
from app.core.db import ensure_indexes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await ensure_indexes()
    print("Database indexes created successfully")
    yield
    # Shutdown
    print("Application shutting down")

app = FastAPI(lifespan=lifespan)
router = APIRouter(prefix="/api")

router.include_router(settings.router)
router.include_router(users.router)

app.include_router(router)
