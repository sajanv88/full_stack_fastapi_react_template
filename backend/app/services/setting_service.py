import logging
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from app.models.settings import StorageSettings, StorageProvider

logger = logging.getLogger(__name__)

class SettingService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.settings_collection: AsyncIOMotorCollection = db.settings

    async def configure_storage(self, setting: dict):
        existing = await self.settings_collection.find_one({"provider": setting["provider"]})
        logger.info(f"Existing setting found: {existing}")
        if existing is None:
            result = await self.settings_collection.insert_one(setting)
            return result.inserted_id
        else:
            # if existing["is_enabled"] != setting["is_enabled"] and setting["is_enabled"]:
            #     logger.info("Disabling other storage providers as a new provider is being enabled.")
            #     await self.settings_collection.update_many({"provider": {"$ne": setting["provider"]}}, {"$set": {"is_enabled": False}})

            logger.info(f"Updating existing setting for provider: {setting['provider']}")
            result = await self.settings_collection.update_one({"_id": ObjectId(existing["_id"])}, {"$set": setting})
            logger.info(f"Update result: {result.modified_count} document(s) modified.")
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
        if setting["provider"] == StorageProvider.AWS_S3.value:
            return {
                "id": str(setting["_id"]),
                "provider": str(setting["provider"]),
                "is_enabled": bool(setting["is_enabled"]),
                "region": str(setting["region"]),
                "aws_access_key": str(setting["aws_access_key"]) if "aws_access_key" in setting else "",
                "aws_secret_key": str(setting["aws_secret_key"]) if "aws_secret_key" in setting else "",
                "aws_bucket_name": str(setting["aws_bucket_name"]) if "aws_bucket_name" in setting else "",
            }
        elif setting["provider"] == StorageProvider.AZURE_BLOB.value:
            return {
                "id": str(setting["_id"]),
                "provider": str(setting["provider"]),
                "is_enabled": bool(setting["is_enabled"]),
                "azure_connection_string": str(setting["azure_connection_string"]) if "azure_connection_string" in setting else "",
                "azure_container_name": str(setting["azure_container_name"]) if "azure_container_name" in setting else "",
            }
        else:
            raise Exception("Unsupported storage provider")
