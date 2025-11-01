from fastapi import APIRouter, Depends, status

from api.core.container import get_notification_banner_service
from api.domain.dtos.notification_settings_dto import CreateNotificationBannerSettingDto, NotificationBannerSettingDto
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.notification_banner_service import NotificationBannerService


router = APIRouter(prefix="/notifications")

router.tags = ["Notifications"]


@router.get("/banner", description="Get the current notification banner information.", response_model=NotificationBannerSettingDto, status_code=status.HTTP_200_OK)
async def get_notification_banner(
    notification_banner_service: NotificationBannerService = Depends(get_notification_banner_service)
):
    return await notification_banner_service.get_banner_setting()

@router.post("/banner", description="Create a new notification banner setting.", response_model=None, status_code=status.HTTP_201_CREATED)
async def create_notification_banner(
    created_banner: CreateNotificationBannerSettingDto,
    current_user: CurrentUser,
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.FULL_ACCESS])),
    notification_banner_service: NotificationBannerService = Depends(get_notification_banner_service)
):
    await notification_banner_service.create_banner_setting(created_banner.is_enabled, created_banner.message, current_user.tenant_id)

@router.put("/banner/{id}", description="Update an existing notification banner setting.", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def update_notification_banner(
    id: str,
    updated_banner: CreateNotificationBannerSettingDto,
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.FULL_ACCESS])),
    notification_banner_service: NotificationBannerService = Depends(get_notification_banner_service)
):
    await notification_banner_service.update_banner_setting(id, updated_banner.is_enabled, updated_banner.message)