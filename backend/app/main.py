from fastapi import FastAPI, APIRouter

from api.routes import settings


app = FastAPI()
router = APIRouter(prefix="/api")

router.include_router(settings.router)

app.include_router(router)
