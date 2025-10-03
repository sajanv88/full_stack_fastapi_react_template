from beanie import PydanticObjectId
from api.common.base_repository import BaseRepository
from api.common.utils import get_logger
from api.domain.entities.storage_settings import StorageProvider, StorageSettings

logger = get_logger(__name__)

class StorageSettingsRepository(BaseRepository[StorageSettings]):
    def __init__(self):
        super().__init__(StorageSettings)

    async def configure_storage(self, setting: StorageSettings) -> PydanticObjectId:
        existing: StorageSettings | None = await self.single_or_none(provider=setting.provider.value)
        logger.info(f"Existing setting found: {existing}")
        if existing is None:
            result = await self.create(data=setting.model_dump())
            return result.id
        
        logger.info(f"Updating existing setting for provider: {setting.provider.value}")
        result = await self.update(id=existing.id, data=setting.model_dump())
        logger.info(f"Update result: {result.id} document(s) modified.")
        return result.id
    
    async def get_storages(self) -> list[StorageSettings]:
        settings = await self.list()
        logger.info(f"Retrieved {len(settings)} storage settings.")
        return settings

    async def get_storage_by_provider(self, provider: StorageProvider) -> StorageSettings | None:
        setting: StorageSettings | None = await self.single_or_none(provider=provider.value)
        if setting is None:
            logger.warning(f"No storage setting found for provider: {provider.value}")
        return setting
    

