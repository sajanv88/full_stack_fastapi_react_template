from typing import Optional

from beanie import PydanticObjectId
from api.domain.dtos.notification_settings_dto import NotificationBannerSettingDto
from api.infrastructure.persistence.repositories.notification_banner_repository_impl import NotificationBannerRepository


class NotificationBannerService:
    def __init__(self, repository: NotificationBannerRepository):
        self.repository: NotificationBannerRepository = repository

    async def get_banner_setting(self) -> NotificationBannerSettingDto:
        result = await self.repository.get_banner_setting()
        if result:
            return NotificationBannerSettingDto(**result.model_dump())
        return NotificationBannerSettingDto(is_enabled=False, message=None)

    async def create_banner_setting(self, is_enabled: bool, message: Optional[str] = None, tenant_id: Optional[PydanticObjectId] = None):
        await self.repository.create_banner_setting(is_enabled, message, tenant_id)

    async def update_banner_setting(self, id: str, is_enabled: bool, message: Optional[str] = None):
        await self.repository.update_banner_setting(id, is_enabled, message)
        
