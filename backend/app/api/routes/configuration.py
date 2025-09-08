from fastapi import  APIRouter
from pydantic import BaseModel

from app.core.utils import is_tenancy_enabled,get_tenancy_strategy

class AppConfigResponse(BaseModel):
    is_multi_tenant_enabled: bool
    multi_tenancy_strategy: str  # "subdomain" or "header"


router = APIRouter(prefix="/config")
router.tags = ["App Config"]

@router.get("/", response_model=AppConfigResponse)
async def get_app_config():

    return AppConfigResponse(
        is_multi_tenant_enabled=is_tenancy_enabled(),
        multi_tenancy_strategy=get_tenancy_strategy()
    )