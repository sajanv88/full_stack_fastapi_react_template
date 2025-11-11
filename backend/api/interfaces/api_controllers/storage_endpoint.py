from typing import List
from fastapi import APIRouter, Depends, status
from api.common.utils import get_logger
from api.core.container import get_storage_settings_service
from api.domain.dtos.storage_settings_dto import AvailableStorageProviderDto, StorageSettingsDto
from api.domain.entities.storage_settings import StorageProvider
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.storage_settings_service import StorageSettingsService


logger = get_logger(__name__)

router = APIRouter(
    prefix="/storage",
    dependencies=[
        Depends(check_permissions_for_current_role(required_permissions=[Permission.MANAGE_STORAGE_SETTINGS]))
    ]
)
router.tags = ["Storage Settings"]

@router.get("/", response_model=List[AvailableStorageProviderDto])
async def get_storage_settings(
    setting_service: StorageSettingsService = Depends(get_storage_settings_service)
):
    return await setting_service.get_storages()

@router.get("/available", response_model=List[dict[str, str]])
async def get_available_providers():
    providers = [{"name": p.value} for p in StorageProvider]
    return providers

@router.post("/configure", status_code=status.HTTP_201_CREATED)
async def configure_storage(
    configuration: StorageSettingsDto,
    current_user: CurrentUser,
    setting_service: StorageSettingsService = Depends(get_storage_settings_service)
):

    logger.debug(f"Received storage configuration: {configuration}")
    try:
        # We don't expect storage settings to be configured with host context as they are global settings. Only tenants with proper permissions can configure them.
        if current_user.tenant_id is None or current_user.tenant_id.strip() == "":
            logger.error("Tenant ID is missing in the current user context.")
            return status.HTTP_400_BAD_REQUEST
        
        await setting_service.configure_storage(setting=configuration)
        return status.HTTP_201_CREATED
    except Exception as e:
        logger.error(f"Failed to configure storage: {e}")
        return status.HTTP_400_BAD_REQUEST
