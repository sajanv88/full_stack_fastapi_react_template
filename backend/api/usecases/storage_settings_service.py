from typing import Optional
from beanie import PydanticObjectId
from api.common.exceptions import NotFoundException
from api.common.utils import get_logger
from api.domain.dtos.storage_settings_dto import AvailableStorageProviderDto, StorageSettingsDto
from api.infrastructure.persistence.repositories.storage_settings_repository_impl import StorageSettingsRepository
from api.domain.entities.storage_settings import StorageProvider, StorageSettings

logger = get_logger(__name__)

class StorageSettingsService:
    def __init__(self, storage_settings_repository: StorageSettingsRepository):
        self.storage_settings_repository = storage_settings_repository


    async def configure_storage(self, setting: StorageSettingsDto, tenant_id: Optional[PydanticObjectId] = None) -> PydanticObjectId:
        settings = StorageSettings(
            provider=setting.provider,
            is_enabled=setting.is_enabled,
            region=setting.region,
            aws_access_key=setting.aws_access_key,
            aws_secret_key=setting.aws_secret_key,
            aws_bucket_name=setting.aws_bucket_name,
            azure_connection_string=setting.azure_connection_string,
            azure_container_name=setting.azure_container_name,
            tenant_id=tenant_id,
            updated_by_user_id=setting.updated_by_user_id
        )
      
        return await self.storage_settings_repository.configure_storage(setting=settings)


    async def get_storages(self) -> list[AvailableStorageProviderDto]:
        return  await self.storage_settings_repository.get_storages()


    async def reset_storage(self, storage_id: str, updated_by_user_id: str, tenant_id: Optional[PydanticObjectId] = None) -> None:
        storage_setting: StorageSettings | None = await self.storage_settings_repository.get(id=storage_id)
        logger.debug(f"Resetting storage setting: {storage_setting}")
        if storage_setting is None:
            raise NotFoundException("StorageSetting", storage_id)
        
        if tenant_id is not None and storage_setting.tenant_id != tenant_id:
            raise NotFoundException("StorageSetting", storage_id)
        
        if storage_setting.provider == StorageProvider.AWS_S3.value:
            storage_setting.aws_access_key = None
            storage_setting.aws_secret_key = None
            storage_setting.aws_bucket_name = None
        elif storage_setting.provider == StorageProvider.AZURE_BLOB.value:
            storage_setting.azure_connection_string = None
            storage_setting.azure_container_name = None

        storage_setting.is_enabled = False
        storage_setting.updated_by_user_id = updated_by_user_id
        await self.storage_settings_repository.reset_storage(id=str(storage_setting.id), data=storage_setting)