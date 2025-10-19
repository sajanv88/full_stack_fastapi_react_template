import json
from beanie import PydanticObjectId
from api.common.base_repository import BaseRepository
from api.common.utils import get_logger
from api.domain.dtos.storage_settings_dto import AvailableStorageProviderDto
from api.domain.entities.storage_settings import StorageProvider, StorageSettings

logger = get_logger(__name__)

class StorageSettingsRepository(BaseRepository[StorageSettings]):
    def __init__(self):
        super().__init__(StorageSettings)

    async def configure_storage(self, setting: StorageSettings) -> PydanticObjectId:
        existing: StorageSettings | None = await self.single_or_none(provider=setting.provider.value)
        logger.info(f"Existing setting found: {existing}")
        if existing is None:
            result = await super().create(data=setting.model_dump())
            return result.id
        
        logger.info(f"Updating existing setting for provider: {setting.provider.value}")
        result = await super().update(id=existing.id, data=setting.model_dump())
        logger.info(f"Update result: {result.id} document(s) modified.")
        return result.id
    
    async def get_storages(self) -> list[AvailableStorageProviderDto]:
        key = self.cache_key("get_storages")
        cached = await self.redis.get(key)
        if cached:
            logger.info(f"Cache hit for key: {key}")
            data = json.loads(cached)
            return [AvailableStorageProviderDto(**item) for item in data]
        logger.info(f"Cache miss for key: {key}. Querying database.")
        settings = await super().list()

        result = []
        for setting in settings:
            serializable = await setting.to_serializable_dict()
            serializable.model_dump(exclude_none=True)
            result.append(serializable)
        await self.set_cache(key, json.dumps([item.model_dump() for item in result]))
        return result

    async def get_storage_by_provider(self, provider: StorageProvider) -> StorageSettings | None:
        setting: StorageSettings | None = await super().single_or_none(provider=provider.value)
        if setting is None:
            logger.warning(f"No storage setting found for provider: {provider.value}")
        return setting
    

