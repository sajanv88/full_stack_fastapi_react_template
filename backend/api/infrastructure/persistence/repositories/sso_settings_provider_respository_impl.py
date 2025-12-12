
from beanie import PydanticObjectId
from api.common.audit_logs_repository import AuditLogRepository
from api.common.base_repository import BaseRepository
from api.domain.entities.sso_settings import SSOSettings


class SSOSettingsProviderRepository(BaseRepository[SSOSettings], AuditLogRepository):
    def __init__(self):
        super().__init__(SSOSettings)


    async def get_by_id(self, id: str) -> SSOSettings | None:
        sso_settings: SSOSettings = await self.get(id=id)
        return sso_settings
    
    async def update_sso_settings(self, id: str, data: SSOSettings) -> SSOSettings | None:
        updated_sso_settings: SSOSettings | None = await super().update(id=id, data=SSOSettings.model_dump(data, exclude_unset=True))
        return updated_sso_settings
    
    async def create_sso_settings(self, data: SSOSettings) -> PydanticObjectId:
        new_sso_settings: SSOSettings = await super().create(data=SSOSettings.model_dump(data))
        return new_sso_settings.id
    
    async def delete_sso_settings(self, id: str) -> bool:
        result: bool =  await super().delete(id=id)
        return result
    
    async def list_sso_settings(self) -> list[SSOSettings]:
        sso_settings_list: list[SSOSettings] = await super().list()
        return sso_settings_list