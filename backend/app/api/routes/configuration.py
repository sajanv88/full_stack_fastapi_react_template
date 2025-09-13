import logging
from typing import Annotated, List, Optional
from fastapi import  APIRouter
from fastapi.params import Depends
from pydantic import BaseModel
from app.core.db import get_db_reference
from app.models.ai_model import AiModel as ModelsResponse
from app.core.ai import  OllamaModels
from app.core.token import TokenData, get_token_decoded_payload
from app.core.utils import is_tenancy_enabled,get_tenancy_strategy, get_host_main_domain_name
from app.models.user_perference import UserPreference
from app.services.user_prefernce_service import UserPreferenceService

logger = logging.getLogger(__name__)
class AppConfigResponse(BaseModel):
    is_multi_tenant_enabled: bool
    multi_tenancy_strategy: str  # "subdomain" or "header"
    host_main_domain: str
    available_ai_models: Optional[List[ModelsResponse]] = []
    is_user_logged_in: Optional[bool] = False
    user_preferences: Optional[UserPreference] = None


router = APIRouter(prefix="/config")
router.tags = ["App Config"]

@router.get("/", response_model=AppConfigResponse)
async def get_app_config(
    user: Annotated[TokenData, Depends(get_token_decoded_payload)],
    db = Depends(get_db_reference)
):
    user_preferences = None
    if user is not None:
        user_preferences_service = UserPreferenceService(db)
        user_preferences = await user_preferences_service.get_user_preference(user_id=user["sub"])

    logger.debug(f"perferences: {user_preferences}")
    return AppConfigResponse(
        is_multi_tenant_enabled=is_tenancy_enabled(),
        multi_tenancy_strategy=get_tenancy_strategy(),
        host_main_domain=get_host_main_domain_name(),
        available_ai_models=OllamaModels().list_models(),
        is_user_logged_in=user is not None,
        user_preferences=user_preferences
    )