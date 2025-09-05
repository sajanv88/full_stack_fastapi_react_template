from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse

from app.api.routes import  users
from app.core.db import ensure_indexes
from app.core.seeder import seed_default_data
from app.api.routes import auth, role, dashboard
import os

build_path = os.path.join(os.path.dirname(__file__), "ui")

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

# Mount static files only if they exist (for production Docker deployment)
if os.path.exists(build_path) and os.path.exists(os.path.join(build_path, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(build_path, "assets")), name="assets")
    print("Static files mounted successfully")
else:
    print("Static files directory not found - running in development mode")

@app.get("/")
async def serve_react_app():
    try:
        if os.path.exists(os.path.join(build_path, "index.html")):
            return FileResponse(os.path.join(build_path, "index.html"))
        else:
            return {"message": "FastAPI backend is running", "mode": "development", "docs": "/docs"}
    except Exception as e:
        print(f"Error serving React app: {e}")
        return {"message": "FastAPI backend is running", "mode": "development", "docs": "/docs"}

router_v1 = APIRouter(prefix="/api/v1")

router_v1.include_router(users.router)
router_v1.include_router(auth.router)
router_v1.include_router(role.router)
router_v1.include_router(dashboard.router)

app.include_router(router_v1)

# Catch-all route for React Router (only in production with static files)
@app.get("/{full_path:path}")
async def react_router(full_path: str):
    if os.path.exists(os.path.join(build_path, "index.html")):
        return FileResponse(os.path.join(build_path, "index.html"))
    else:
        return {"message": "API endpoint not found", "available_docs": "/docs", "api_base": "/api/v1"}
