from typing import List
from fastapi import APIRouter, Depends
from api.common.utils import get_logger
from api.core.container import get_storage_settings_service
from api.domain.dtos.storage_settings_dto import AvailableStorageProviderDTO
from api.domain.entities.storage_settings import StorageProvider
from api.domain.enum.permission import Permission
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.storage_settings_service import StorageSettingsService


logger = get_logger(__name__)

router = APIRouter(prefix="/storage")
router.tags = ["Storage Settings"]


@router.get("/", response_model=List[AvailableStorageProviderDTO])
async def get_storage_settings(
    setting_service: StorageSettingsService = Depends(get_storage_settings_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.MANAGE_STORAGE_SETTINGS]))
):
    return await setting_service.get_storages()

@router.get("/available", response_model=List[dict[str, str]])
async def get_available_providers(
    setting_service: StorageSettingsService = Depends(get_storage_settings_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.MANAGE_STORAGE_SETTINGS]))
):
    providers = [{"name": p.value} for p in StorageProvider]
    return providers
