from fastapi import FastAPI, APIRouter
from contextlib import asynccontextmanager

from app.api.routes import  users
from app.core.db import ensure_indexes, seed_default_data
from app.api.routes import auth, role

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await ensure_indexes()
    print("Database indexes created successfully")
    await seed_default_data()
    print("Default data seeded successfully")
    yield
    # Shutdown
    print("Application shutting down")

app = FastAPI(lifespan=lifespan)
router_v1 = APIRouter(prefix="/api/v1")

router_v1.include_router(users.router)
router_v1.include_router(auth.router)
router_v1.include_router(role.router)

app.include_router(router_v1)
