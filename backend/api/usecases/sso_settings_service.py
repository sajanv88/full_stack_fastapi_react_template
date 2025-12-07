from typing import List
from typing_extensions import get_args
from api.common.utils import get_logger, get_sso_redirect_uri
from api.domain.dtos.sso_settings_dto import CreateSSOSettingsDto, ReadSSOSettingsDto, SSOSettingsListDto, UpdateSSOSettingsDto
from api.domain.entities.sso_settings import SSOProvider, SSOSettings
from api.infrastructure.persistence.repositories.sso_settings_provider_respository_impl import SSOSettingsProviderRepository
from api.usecases.tenant_service import TenantService

logger = get_logger(__name__)

class SSOSettingsService:
    def __init__(self, sso_settings_provider_repository: SSOSettingsProviderRepository, tenant_service: TenantService):
        self.sso_settings_provider_repository: SSOSettingsProviderRepository = sso_settings_provider_repository
        self.tenant_service: TenantService = tenant_service

    async def get_sso_settings_by_id(self, id: str) -> ReadSSOSettingsDto:
        res = await self.sso_settings_provider_repository.get_by_id(id)
        return ReadSSOSettingsDto(**res.model_dump(exclude={"client_secret": True}))

    async def update_redirect_uri(self, id: str, redirect_uri: str) -> None:
        await self.sso_settings_provider_repository.update_sso_settings(id, SSOSettings(redirect_uris=[redirect_uri]))

    async def update_sso_settings(self, id: str, sso_settings: UpdateSSOSettingsDto) -> None:
        await self.sso_settings_provider_repository.update_sso_settings(id, SSOSettings(**sso_settings.model_dump(exclude_none=True, exclude_unset=True)))

    async def create_sso_settings(self, sso_settings: CreateSSOSettingsDto) -> str:
        redirect_uri = get_sso_redirect_uri(sso_settings.provider)
        if sso_settings.tenant_id:
            tenant = await self.tenant_service.get_tenant_by_id(tenant_id=sso_settings.tenant_id)
            redirect_uri = get_sso_redirect_uri(sso_settings.provider, tenant.custom_domain if tenant.custom_domain else tenant.subdomain)

        sso_settings.redirect_uris = [redirect_uri]    
        res = await self.sso_settings_provider_repository.create_sso_settings(SSOSettings(**sso_settings.model_dump()))
        return str(res)
    
    async def delete_sso_settings(self, id: str) -> bool:
        return await self.sso_settings_provider_repository.delete_sso_settings(id)
    
    async def list(self) -> SSOSettingsListDto:
        ssos: List[SSOSettings] = await self.sso_settings_provider_repository.list_sso_settings()
        logger.info(f"Retrieved {len(ssos)} SSO settings from repository")
        logger.debug(f"SSO Settings: {ssos}")
        items = [ReadSSOSettingsDto(**sso.model_dump(exclude={"client_secret": True})) for sso in ssos]
        return SSOSettingsListDto(items=items)
    
    async def get_provider(self, provider_name: SSOProvider) -> SSOSettings:
        ssos: List[SSOSettings] = await self.sso_settings_provider_repository.list_sso_settings()
        for sso in ssos:
            if sso.provider == provider_name:
                return sso
        raise ValueError(f"SSO provider '{provider_name}' not found or not enabled.")
    
    async def get_only_enabled_providers(self) -> SSOSettingsListDto:
        ssos: List[SSOSettings] = await self.sso_settings_provider_repository.list_sso_settings()
        enabled_ssos = [sso for sso in ssos if sso.enabled]
        items = [ReadSSOSettingsDto(**sso.model_dump(exclude={"client_secret": True})) for sso in enabled_ssos]
        return SSOSettingsListDto(items=items)
    
    async def get_available_sso_providers(self) -> List[str]:
        return list(get_args(SSOProvider))