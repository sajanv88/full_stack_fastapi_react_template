from api.domain.dtos.sso_settings_dto import CreateSSOSettingsDto, ReadSSOSettingsDto, SSOSettingsDto, SSOSettingsListDto, UpdateSSOSettingsDto
from api.domain.entities.sso_settings import SSOSettings
from api.infrastructure.persistence.repositories.sso_settings_provider_respository_impl import SSOSettingsProviderRepository


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
    
    async def list_sso_settings(self) -> SSOSettingsListDto:
        ssos = await self.sso_settings_provider_repository.list_sso_settings()
        items = [ReadSSOSettingsDto(**sso.model_dump(exclude={"client_secret"})) for sso in ssos]
        return SSOSettingsListDto(items=items)