from http.client import HTTPException
import logging
from typing import Annotated, List
from fastapi import APIRouter, Depends, Response, status

from app.api.routes.auth import get_current_user
from app.core.db import get_db_reference
from app.core.permission import Permission
from app.core.role_checker import create_permission_checker
from app.models.settings import StorageSettings, StorageProvider
from app.models.user import User
from app.services.setting_service import SettingService
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/storage")
router.tags = ["Storage Settings"]
    
@router.get("/", response_model=List[StorageSettings])
async def get_storage_settings(
    current_user: Annotated[User, Depends(get_current_user)],
    db = Depends(get_db_reference),
    _: bool = Depends(create_permission_checker([Permission.MANAGE_STORAGE_SETTINGS]))
):
    setting_service = SettingService(db)
    return await setting_service.get_storages()

@router.get("/available", response_model=List[dict[str, str]])
async def get_available_providers(
    current_user: Annotated[User, Depends(get_current_user)],
    db = Depends(get_db_reference),
    _: bool = Depends(create_permission_checker([Permission.MANAGE_STORAGE_SETTINGS]))
):
    providers = [{"name": p.value} for p in StorageProvider]
    return providers


@router.post("/configure", status_code=status.HTTP_201_CREATED)
async def configure_storage(
    current_user: Annotated[User, Depends(get_current_user)],
    configuration: StorageSettings,
    db = Depends(get_db_reference),
    _: bool = Depends(create_permission_checker([Permission.MANAGE_STORAGE_SETTINGS]))
):
    try:
        setting_service = SettingService(db)
        setting_dict = {
            "provider": configuration.provider,
            "region": configuration.region,
            "access_key": configuration.access_key,
            "secret_key": configuration.secret_key,
            "connection_string": configuration.connection_string,
            "is_enabled": configuration.is_enabled
        }
        await setting_service.configure_storage(setting=setting_dict)
        return Response(status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(status=status.HTTP_400_BAD_REQUEST, detail=str(e))