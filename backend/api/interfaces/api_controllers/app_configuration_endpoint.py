
from fastapi import APIRouter, Depends, status

from api.common.dtos.app_configuration_dto import AppConfigurationDto
from api.common.utils import get_host_main_domain_name, get_logger, get_tenancy_strategy, is_tenancy_enabled
from api.core.container import   get_passkey_service,  get_tenant_service, get_user_preference_service
from api.core.exceptions import  TenantNotFoundException
from api.domain.dtos.tenant_dto import TenantDto
from api.domain.entities.tenant import Tenant
from api.infrastructure.externals.local_ai_model import OllamaModels
from api.infrastructure.security.current_user import  CurrentUserOptional
from api.infrastructure.security.passkey_service import PasskeyService
from api.interfaces.middlewares.tenant_middleware import get_tenant_id
from api.usecases.tenant_service import TenantService
from api.usecases.user_preference_service import UserPreferenceService
from api.core.config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/app_configuration")
router.tags = ["App Configuration"]

async def get_tenant(service: TenantService, tenant_id: str | None) -> Tenant | None:
    current_tenant = None
    logger.debug(f"Fetching tenant with ID: {tenant_id}")
    try:
        t = await service.get_tenant_by_id(tenant_id)
        current_tenant = Tenant(**t.model_dump())
    except TenantNotFoundException:
        logger.warning(f"Tenant with ID {tenant_id} not found for current user.")
        current_tenant = None
    finally:
        return current_tenant

@router.get("/", response_model=AppConfigurationDto, status_code=status.HTTP_200_OK)
async def get_app_configuration(
    current_user: CurrentUserOptional,
    tenant_id =  Depends(get_tenant_id),
    user_pref_service: UserPreferenceService = Depends(get_user_preference_service),
    tenant_service: TenantService = Depends(get_tenant_service),
    passkey_service: PasskeyService = Depends(get_passkey_service)
):
    user_pref_doc = None
    current_tenant = None
    is_user_logged_in = False
    if current_user is not None:
        user_preferences = await user_pref_service.get_preferences(user_id=current_user.id)
        user_pref_doc = await user_preferences.to_serializable_dict() if user_preferences is not None else None
        is_user_logged_in = True
        passkey_enabled = await passkey_service.has_passkeys(email=current_user.email)
        if user_pref_doc is not None:
            user_pref_doc.setdefault("preferences", {})["passkey_enabled"] = passkey_enabled

    tenant_id = str(current_user.tenant_id) if current_user and current_user.tenant_id else str(tenant_id) if tenant_id else None
    t = await get_tenant(tenant_service, str(tenant_id))
    current_tenant = TenantDto(**t.model_dump()) if t else None

   
    

    # Fetch available AI models from Ollama
    available_ai_models = OllamaModels().list_models()
    return AppConfigurationDto(
        is_multi_tenant_enabled=is_tenancy_enabled(),
        multi_tenancy_strategy=get_tenancy_strategy(),
        host_main_domain=get_host_main_domain_name(),
        available_ai_models=available_ai_models,
        is_user_logged_in=is_user_logged_in,
        user_preferences=user_pref_doc,
        current_tenant=current_tenant,
        environment = settings.fastapi_env,

    )

