from fastapi import APIRouter, Depends, status

from api.common.dtos.app_configuration_dto import AppConfigurationDto
from api.common.utils import get_host_main_domain_name, get_logger, get_tenancy_strategy, is_tenancy_enabled
from api.core.container import  get_tenant_service, get_user_preference_service
from api.core.exceptions import TenantNotFoundException
from api.infrastructure.externals.local_ai_model import OllamaModels
from api.infrastructure.security.current_user import  CurrentUserOptional
from api.usecases.tenant_service import TenantService
from api.usecases.user_preference_service import UserPreferenceService

logger = get_logger(__name__)

router = APIRouter(prefix="/app_configuration")
router.tags = ["App Configuration"]

@router.get("/", response_model=AppConfigurationDto, status_code=status.HTTP_200_OK)
async def get_app_configuration(
    current_user: CurrentUserOptional,
    user_pref_service: UserPreferenceService = Depends(get_user_preference_service),
    tenant_service: TenantService = Depends(get_tenant_service)
):
    user_pref_doc = None
    current_tenant = None
    if current_user is not None:
        user_preferences = await user_pref_service.get_preferences(user_id=current_user.id)
        user_pref_doc = await user_preferences.to_serializable_dict() if user_preferences is not None else None
        if current_user.tenant_id:
            try:
                tenant = await tenant_service.get_tenant_by_id(current_user.tenant_id)
                current_tenant = await tenant.to_serializable_dict()
            except TenantNotFoundException:
                logger.warning(f"Tenant with ID {current_user.tenant_id} not found for current user.")
                current_tenant = None
    
     # Fetch available AI models from Ollama
    available_ai_models = OllamaModels().list_models()
    return AppConfigurationDto(
        is_multi_tenant_enabled=is_tenancy_enabled(),
        multi_tenancy_strategy=get_tenancy_strategy(),
        host_main_domain=get_host_main_domain_name(),
        available_ai_models=available_ai_models,
        is_user_logged_in=False,
        user_preferences=user_pref_doc,
        current_tenant=current_tenant
    )




