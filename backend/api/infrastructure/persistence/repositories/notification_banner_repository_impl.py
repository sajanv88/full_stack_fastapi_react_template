from beanie import PydanticObjectId
from api.common.base_repository import BaseRepository
from api.common.exceptions import NotFoundException
from api.domain.entities.notification_settings import NotificationBannerSetting


class NotificationBannerRepository(BaseRepository[NotificationBannerSetting]):
    def __init__(self):
        super().__init__(NotificationBannerSetting)
    
    async def get_banner_setting(self) -> NotificationBannerSetting | None:
        result = await self.list()
        if len(result) == 0:
            return None
        setting = result[0]
        return NotificationBannerSetting(**setting.model_dump())

    async def create_banner_setting(self, is_enabled: bool, message: str | None, tenant_id: PydanticObjectId | None) -> NotificationBannerSetting:
        new_setting = NotificationBannerSetting(is_enabled=is_enabled, message=message, tenant_id=tenant_id)
        created_setting = await self.create(new_setting.model_dump())
        return created_setting
    
    async def update_banner_setting(self, id: str, is_enabled: bool, message: str | None) -> NotificationBannerSetting | None:
        exisiting_setting = await self.get(id)
        if not exisiting_setting:
            raise NotFoundException("NotificationBannerSetting", id)
        exisiting_setting.is_enabled = is_enabled
        exisiting_setting.message = message
        
        updated_setting = await self.update(id, exisiting_setting.model_dump(exclude_none=True))
        return updated_setting