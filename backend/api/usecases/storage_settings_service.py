from beanie import PydanticObjectId
from api.infrastructure.persistence.repositories.storage_settings_repository_impl import StorageSettingsRepository
from api.domain.dtos.storage_settings_dto import AvailableStorageProviderDTO, StorageSettingsDTO
from api.domain.entities.storage_settings import StorageSettings

class StorageSettingsService:
    def __init__(self, storage_settings_repository: StorageSettingsRepository):
        self.storage_settings_repository = storage_settings_repository


    async def configure_storage(self, setting: StorageSettingsDTO) -> PydanticObjectId:
        settings = StorageSettings(
            provider=setting.provider,
            is_enabled=setting.is_enabled,
            region=setting.region,
            aws_access_key=setting.aws_access_key,
            aws_secret_key=setting.aws_secret_key,
            aws_bucket_name=setting.aws_bucket_name,
            azure_connection_string=setting.azure_connection_string,
            azure_container_name=setting.azure_container_name
        )
        return await self.storage_settings_repository.configure_storage(setting=settings)


    async def get_storages(self) -> list[AvailableStorageProviderDTO]:
        settings = await self.storage_settings_repository.get_storages()
        result: list[AvailableStorageProviderDTO] = []
        for setting in settings:
            serializable = await setting.to_serializable_dict()
            result.append(serializable)
        return result