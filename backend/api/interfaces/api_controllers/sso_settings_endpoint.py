from typing import List
from fastapi import APIRouter, Depends
from api.common.utils import get_logger
from api.core.container import get_sso_settings_service
from api.domain.dtos.sso_settings_dto import CreateSSOSettingsDto, ReadSSOSettingsDto, SSOSettingsDto, SSOSettingsListDto, UpdateSSOSettingsDto
from api.domain.enum.permission import Permission
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.sso_settings_service import SSOSettingsService


logger = get_logger(__name__)

router = APIRouter(prefix="/ssos", tags=["SSO Settings"], dependencies=[Depends(check_permissions_for_current_role(required_permissions=[Permission.FULL_ACCESS]))])

@router.get("/", response_model=SSOSettingsListDto, response_model_exclude_none=True)
async def list(
    sso_settings_service: SSOSettingsService = Depends(get_sso_settings_service)
):
    logger.info("Listing SSO settings")
    return await sso_settings_service.list()


@router.get("/{sso_id}", response_model=ReadSSOSettingsDto, response_model_exclude_none=True)
async def get_sso_settings_by_id(
    sso_id: str,
    sso_settings_service: SSOSettingsService = Depends(get_sso_settings_service)
):
    logger.info(f"Getting SSO settings by ID: {sso_id}")
    return await sso_settings_service.get_sso_settings_by_id(sso_id)

@router.post("/", response_model=str)
async def create_sso_settings(
    sso_settings: CreateSSOSettingsDto,
    sso_settings_service: SSOSettingsService = Depends(get_sso_settings_service)
):
    logger.info("Creating new SSO settings")
    return await sso_settings_service.create_sso_settings(sso_settings)

@router.delete("/{sso_id}", response_model=bool)
async def delete_sso_settings(
    sso_id: str,
    sso_settings_service: SSOSettingsService = Depends(get_sso_settings_service)
):
    logger.info(f"Deleting SSO settings by ID: {sso_id}")
    return await sso_settings_service.delete_sso_settings(sso_id)


@router.patch("/{sso_id}", response_model=None)
async def update_sso_settings(
    sso_id: str,
    sso_settings: UpdateSSOSettingsDto,
    sso_settings_service: SSOSettingsService = Depends(get_sso_settings_service)
):
    logger.info(f"Updating SSO settings by ID: {sso_id}")
    await sso_settings_service.update_sso_settings(sso_id, sso_settings)