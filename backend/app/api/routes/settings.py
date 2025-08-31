from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter(prefix="/settings")

class Configuration(BaseModel):
    name: str
    version: str
    is_authenticated: bool


class Settings(BaseModel):
    key: str
    value: Configuration

@router.get("/", response_model=Settings)
def load_settings():
    return Settings(key="config", value=Configuration(name="Full-Stack App", version="1.0", is_authenticated=False))