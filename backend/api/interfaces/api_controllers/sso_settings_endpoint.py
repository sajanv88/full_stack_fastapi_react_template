from typing import List
from fastapi import APIRouter, Depends, status
from api.common.utils import get_logger
from api.core.container import get_sso_settings_service
from api.domain.dtos.sso_settings_dto import CreateSSOSettingsDto, ReadSSOSettingsDto, SSOSettingsListDto, SSOSettingsResponseDto, UpdateSSOSettingsDto
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.sso_settings_service import SSOSettingsService


logger = get_logger(__name__)

router = APIRouter(prefix="/ssos", tags=["SSO Settings"], dependencies=[Depends(check_permissions_for_current_role(required_permissions=[Permission.FULL_ACCESS]))])

@router.get("/", response_model=SSOSettingsListDto, response_model_exclude_none=True)
async def list(
    sso_settings_service: SSOSettingsService = Depends(get_sso_settings_service)
):
    return await sso_settings_service.list()

@router.get("/available-providers", response_model=List)
async def get_available_sso_providers(
    sso_settings_service: SSOSettingsService = Depends(get_sso_settings_service)
):
    return await sso_settings_service.get_available_sso_providers()

@router.get("/{sso_id}", response_model=ReadSSOSettingsDto, response_model_exclude_none=True)
async def get_sso_settings_by_id(
    sso_id: str,
    sso_settings_service: SSOSettingsService = Depends(get_sso_settings_service)
):
    return await sso_settings_service.get_sso_settings_by_id(sso_id)

@router.post("/", response_model=SSOSettingsResponseDto, status_code=status.HTTP_201_CREATED)
async def create_sso_settings(
    current_user: CurrentUser,
    sso_settings: CreateSSOSettingsDto,
    sso_settings_service: SSOSettingsService = Depends(get_sso_settings_service)
):
    sso_settings.tenant_id = current_user.tenant_id if current_user.tenant_id else None
    await sso_settings_service.create_sso_settings(sso_settings)
    return SSOSettingsResponseDto(message="SSO settings created successfully")

@router.delete("/{sso_id}", response_model=bool)
async def delete_sso_settings(
    sso_id: str,
    sso_settings_service: SSOSettingsService = Depends(get_sso_settings_service)
):
    return await sso_settings_service.delete_sso_settings(sso_id)


@router.patch("/{sso_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def update_sso_settings(
    sso_id: str,
    sso_settings: UpdateSSOSettingsDto,
    sso_settings_service: SSOSettingsService = Depends(get_sso_settings_service)
):
    await sso_settings_service.update_sso_settings(sso_id, sso_settings)
    return None
