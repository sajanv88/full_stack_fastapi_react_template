from fastapi import APIRouter, Depends, status

from api.common.dtos.app_configuration_dto import AppConfigurationDto
from api.common.utils import get_host_main_domain_name, get_logger, get_tenancy_strategy, is_tenancy_enabled
from api.core.container import  get_user_preference_service
from api.infrastructure.externals.local_ai_model import OllamaModels
from api.infrastructure.security.current_user import  CurrentUserOptional
from api.usecases.user_preference_service import UserPreferenceService

logger = get_logger(__name__)

router = APIRouter(prefix="/app_configuration")
router.tags = ["App Configuration"]

@router.get("/", response_model=AppConfigurationDto, status_code=status.HTTP_200_OK)
async def get_app_configuration(
    current_user: CurrentUserOptional,
    user_pref_service: UserPreferenceService = Depends(get_user_preference_service)
):
    user_pref_doc = None
    if current_user is not None:
        user_preferences = await user_pref_service.get_preferences(user_id=current_user.id)
        user_pref_doc = await user_preferences.to_serializable_dict() if user_preferences is not None else None


     # Fetch available AI models from Ollama
    available_ai_models = OllamaModels().list_models()
    return AppConfigurationDto(
        is_multi_tenant_enabled=is_tenancy_enabled(),
        multi_tenancy_strategy=get_tenancy_strategy(),
        host_main_domain=get_host_main_domain_name(),
        available_ai_models=available_ai_models,
        is_user_logged_in=False,
        user_preferences=user_pref_doc
    )




