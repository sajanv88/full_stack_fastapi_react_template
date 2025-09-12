from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
import logging

from app.core.storage import AzureBlobStorage, S3Storage
from app.models.settings import StorageProvider

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.settings_collection: AsyncIOMotorCollection = db.settings

    async def get_active_provider(self):
        active_provider = await self.settings_collection.find_one({"is_enabled": True})
        if active_provider is None:
            raise Exception("No enabled storage provider found")
        return active_provider
    
    async def bucket_or_container_name(self) -> str:
        active_provider = await self.get_active_provider()
        if active_provider["provider"] == StorageProvider.AWS_S3.value:
            return active_provider["aws_bucket_name"]
        elif active_provider["provider"] == StorageProvider.AZURE_BLOB.value:
            return active_provider["azure_container_name"]
        else:
            raise Exception(f"Unsupported storage provider: {active_provider['provider']}")

    async def upload_file(self, file: UploadFile):
        active_provider = await self.settings_collection.find_one({"is_enabled": True})
        if active_provider is None:
            raise Exception("No enabled storage provider found")

        if active_provider["provider"] == StorageProvider.AWS_S3.value:
            logger.info(f"Uploading file to AWS S3: {file.filename}")
            s3 = S3Storage(
                bucket_name=active_provider["aws_bucket_name"],
                aws_access_key=active_provider["aws_access_key"],
                aws_secret_key=active_provider["aws_secret_key"],
                region=active_provider["region"]
            )
            return await s3.upload_file(file, active_provider["aws_bucket_name"] + "/" + file.filename)
        elif active_provider["provider"] == StorageProvider.AZURE_BLOB.value:
            logger.info(f"Uploading file to Azure Blob Storage: {file.filename}")
            azure = AzureBlobStorage(
                connection_string=active_provider["azure_connection_string"],
                container_name=active_provider["azure_container_name"]
            )
            return await azure.upload_file(file, active_provider["azure_container_name"] + "/" + file.filename)
        else:
            raise Exception(f"Unsupported storage provider: {active_provider['provider']}")
        
    async def generate_read_url(self, file_key: str, expires_in: int = 3600) -> str:
        active_provider = await self.settings_collection.find_one({"is_enabled": True})
        if active_provider is None:
            raise Exception("No enabled storage provider found")

        if active_provider["provider"] == StorageProvider.AWS_S3.value:
            s3 = S3Storage(
                bucket_name=active_provider["aws_bucket_name"],
                aws_access_key=active_provider["aws_access_key"],
                aws_secret_key=active_provider["aws_secret_key"],
                region=active_provider["region"]
            )
            return await s3.generate_read_url(file_key, expires_in)
        elif active_provider["provider"] == StorageProvider.AZURE_BLOB.value:
            azure = AzureBlobStorage(
                connection_string=active_provider["azure_connection_string"],
                container_name=active_provider["azure_container_name"]
            )
            return await azure.generate_read_url(file_key, expires_in)
        else:
            raise Exception(f"Unsupported storage provider: {active_provider['provider']}")
