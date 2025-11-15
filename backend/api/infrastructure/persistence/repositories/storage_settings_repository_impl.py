from beanie import PydanticObjectId
from api.common.audit_logs_repository import AuditLogRepository
from api.common.base_repository import BaseRepository
from api.common.utils import get_logger
from api.domain.dtos.audit_logs_dto import AuditLogDto
from api.domain.dtos.storage_settings_dto import AvailableStorageProviderDto
from api.domain.entities.storage_settings import StorageProvider, StorageSettings

logger = get_logger(__name__)

class StorageSettingsRepository(BaseRepository[StorageSettings], AuditLogRepository):
    def __init__(self):
        super().__init__(StorageSettings)


    async def configure_storage(self, setting: StorageSettings) -> PydanticObjectId:
        existing: StorageSettings | None = await self.single_or_none(provider=setting.provider.value)
        if existing is None:
            result = await super().create(data=setting.model_dump())
            sett: StorageSettings = await super().get(result.id)
            await self.add_audit_log(AuditLogDto(
                action="create",
                changes={"Info": f"Created a new storage settings with {setting.provider.value} and {result.id}"},
                entity="StorageSettings",
                tenant_id=str(sett.tenant_id) if sett.tenant_id else None,
                user_id=setting.updated_by_user_id
            ))
            return result.id
        
        logger.info(f"Updating existing setting for provider: {setting.provider.value}")
        result = await super().update(id=str(existing.id), data=setting.model_dump())
        logger.info(f"Update result: {result.id} document(s) modified.")
        is_enabled_change = existing.is_enabled != setting.is_enabled
        region_change = existing.region != setting.region
        changes = {}
        if is_enabled_change:
            changes["is_enabled"] = {"from": existing.is_enabled, "to": setting.is_enabled}
        if region_change:
            changes["region"] = {"from": existing.region, "to": setting.region}

        await self.add_audit_log(AuditLogDto(
                action="update",
                changes={"Info": f"Updated storage settings with {setting.provider.value} and {result.id}" , **changes},
                entity="StorageSettings",
                tenant_id=str(setting.tenant_id) if setting.tenant_id else None,
                user_id=setting.updated_by_user_id
            ))
        return result.id
    
    async def get_storages(self) -> list[AvailableStorageProviderDto]:
        settings = await super().list()
        result = []
        for setting in settings:
            serializable = await setting.to_serializable_dict()
            serializable.model_dump(exclude_none=True)
            result.append(serializable)
        return result

    async def get_storage_by_provider(self, provider: StorageProvider) -> StorageSettings | None:
        setting: StorageSettings | None = await super().single_or_none(provider=provider.value)
        if setting is None:
            logger.warning(f"No storage setting found for provider: {provider.value}")
        return setting
    

