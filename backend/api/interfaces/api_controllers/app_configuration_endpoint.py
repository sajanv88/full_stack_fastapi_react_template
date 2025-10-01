from fastapi import APIRouter, Depends, status

from api.common.dtos.app_configuration_dto import AppConfigurationDto
from api.common.utils import get_host_main_domain_name, get_logger, get_tenancy_strategy, is_tenancy_enabled
from api.core.container import  get_user_preference_service
from api.infrastructure.externals.local_ai_model import OllamaModels
from api.usecases.user_preference_service import UserPreferenceService

logger = get_logger(__name__)

router = APIRouter(prefix="/app_configuration")
router.tags = ["App Configuration"]

@router.get("/", response_model=AppConfigurationDto, status_code=status.HTTP_200_OK)
async def get_app_configuration(
    user_pref_service: UserPreferenceService = Depends(get_user_preference_service)
):
    # Temporarily using a hardcoded user ID until authentication is implemented
    user_preferences = await user_pref_service.get_preferences(user_id="68c302ef6bf7a039b7e9b385")
  
    user_pref_doc = await user_preferences.to_serializable_dict() if user_preferences is not None else None
    logger.debug(f"User preferences: {user_pref_doc}")
    available_ai_models = OllamaModels().list_models()
    return AppConfigurationDto(
        is_multi_tenant_enabled=is_tenancy_enabled(),
        multi_tenancy_strategy=get_tenancy_strategy(),
        host_main_domain=get_host_main_domain_name(),
        available_ai_models=available_ai_models,
        is_user_logged_in=False,
        user_preferences=user_pref_doc
    )




