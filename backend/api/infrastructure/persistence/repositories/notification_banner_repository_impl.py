from beanie import PydanticObjectId
from api.common.audit_logs_repository import AuditLogRepository
from api.common.base_repository import BaseRepository
from api.common.exceptions import NotFoundException
from api.domain.dtos.audit_logs_dto import AuditLogDto
from api.domain.entities.notification_settings import NotificationBannerSetting


class NotificationBannerRepository(BaseRepository[NotificationBannerSetting], AuditLogRepository):
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
        await self.add_audit_log(AuditLogDto(
            action="create",
            changes={"info": f"Created notification banner setting for tenant {tenant_id}"},
            entity="NotificationBannerSetting",
            tenant_id=str(tenant_id) if tenant_id else None,
            user_id=None  # Todo: Need to add a new property in role.. to determine who added it.
        ))
        return created_setting
    
    async def update_banner_setting(self, id: str, is_enabled: bool, message: str | None) -> NotificationBannerSetting | None:
        exisiting_setting = await self.get(id)
        if not exisiting_setting:
            await self.add_audit_log(AuditLogDto(
                action="error",
                changes={"info": f"Attempted to update non-existing notification banner setting with id {id}"},
                entity="NotificationBannerSetting",
                tenant_id=None,
                user_id=None  # Todo: Need to add a new property in role.. to determine who updated it.
            ))
            raise NotFoundException("NotificationBannerSetting", id)
        exisiting_setting.is_enabled = is_enabled
        exisiting_setting.message = message
        
        updated_setting = await self.update(id, exisiting_setting.model_dump(exclude_none=True))
        await self.add_audit_log(AuditLogDto(
            action="update",
            changes={"new": updated_setting.model_dump(exclude_none=True), "old": exisiting_setting.model_dump(exclude_none=True)},
            entity="NotificationBannerSetting",
            tenant_id=str(exisiting_setting.tenant_id) if exisiting_setting.tenant_id else None,
            user_id=None  # Todo: Need to add a new property in role.. to determine who updated it.
        ))
        return updated_setting