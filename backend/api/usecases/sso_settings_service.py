from typing import List
from api.common.utils import get_logger
from api.domain.dtos.sso_settings_dto import CreateSSOSettingsDto, ReadSSOSettingsDto, SSOSettingsListDto, UpdateSSOSettingsDto
from api.domain.entities.sso_settings import SSOProvider, SSOSettings
from api.infrastructure.persistence.repositories.sso_settings_provider_respository_impl import SSOSettingsProviderRepository

logger = get_logger(__name__)

class SSOSettingsService:
    def __init__(self, sso_settings_provider_repository: SSOSettingsProviderRepository):
        self.sso_settings_provider_repository: SSOSettingsProviderRepository = sso_settings_provider_repository

    async def get_sso_settings_by_id(self, id: str) -> ReadSSOSettingsDto:
        res = await self.sso_settings_provider_repository.get_by_id(id)
        return ReadSSOSettingsDto(**res.model_dump(exclude={"client_secret"}))

    async def update_sso_settings(self, id: str, sso_settings: UpdateSSOSettingsDto) -> None:
        await self.sso_settings_provider_repository.update_sso_settings(id, SSOSettings(**sso_settings.model_dump()))

    async def create_sso_settings(self, sso_settings: CreateSSOSettingsDto) -> str:
        return str(await self.sso_settings_provider_repository.create_sso_settings(SSOSettings(**sso_settings.model_dump())))
    
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