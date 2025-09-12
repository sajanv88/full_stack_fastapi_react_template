import logging
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from app.models.settings import StorageSettings, StorageProvider

logger = logging.getLogger(__name__)

class SettingService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.settings_collection: AsyncIOMotorCollection = db.settings

    async def configure_storage(self, setting: dict):
        existing = await self.settings_collection.find_one({"provider": setting["provider"]})
        if existing is None:
            
            result = await self.settings_collection.insert_one(setting)
            return result.inserted_id
        else:
            result = await self.settings_collection.update_one({"provider": setting["provider"]}, update=setting)
            return result.modified_count

    async def get_storage_by_provider(self, provider: StorageProvider) -> StorageSettings:

        result = await self.settings_collection.find_one({"provider": provider.value})
        if result is None:
            raise Exception("No provider found!")
        return self.serialize(result)
    
    
    async def get_storages(self):
        result = await self.settings_collection.find().to_list()
        if len(result) > 0:
            return [await self.serialize(setting) for setting in result]
        return []

    async def serialize(self, setting: dict):
        return {
            "id": str(setting["_id"]),
            "provider": str(setting["provider"]),
            "is_enabled": bool(setting["is_enabled"]),
            "region": str(setting["region"]),
            "access_key": str(setting["access_key"]),
            "secret_key": str(setting["secret_key"]),
            "connection_string": str(setting["connection_string"])
        }
