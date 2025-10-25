from fastapi import UploadFile

from api.common.utils import get_logger
from api.core.exceptions import StorageNotEnabledException
from api.domain.entities.storage_settings import StorageProvider, StorageSettings
from api.infrastructure.externals.azure_storage import AzureBlobStorage
from api.infrastructure.externals.s3_storage import S3Storage
from api.core.config import settings

logger = get_logger(__name__)

class FileUpload:
    def __init__(self):
        from api.core.container import get_storage_settings_repository # To avoid circular imports
        self.storage_repository = get_storage_settings_repository()

    
    async def upload_file(self, file: UploadFile) -> str:
        active_provider: StorageSettings = await self.storage_repository.single_or_none(is_enabled=True)
        try:
            if active_provider is None:
                raise StorageNotEnabledException()

            if active_provider.provider.value == StorageProvider.AWS_S3.value:
                logger.info(f"Uploading file to AWS S3: {file.filename}")   
                s3 = S3Storage(
                    bucket_name=active_provider.aws_bucket_name,
                    aws_access_key=active_provider.aws_access_key,
                    aws_secret_key=active_provider.aws_secret_key,
                    region=active_provider.region
                )
                return await s3.upload_file(file, active_provider.aws_bucket_name + "/" + file.filename)
            elif active_provider.provider.value == StorageProvider.AZURE_BLOB.value:
                logger.info(f"Uploading file to Azure Blob Storage: {file.filename}")
                azure = AzureBlobStorage(
                    connection_string=active_provider.azure_connection_string,
                    container_name=active_provider.azure_container_name
                )
                return await azure.upload_file(file, active_provider.azure_container_name + "/" + file.filename)
            else:
                raise StorageNotEnabledException()
                
        except StorageNotEnabledException as se:
            logger.warning(f"Unsupported storage provider: {str(se)}, Hence using default S3 storage")
            s3 = S3Storage(
                bucket_name=settings.aws_s3_bucket_name,
                aws_access_key=settings.aws_access_key_id,
                aws_secret_key=settings.aws_secret_access_key,
                region=settings.aws_region
            )
            return await s3.upload_file(file, settings.aws_s3_bucket_name + "/" + file.filename)
