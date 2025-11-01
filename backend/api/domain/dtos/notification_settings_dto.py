from pydantic import BaseModel


class NotificationBannerSettingDto(BaseModel):
    is_enabled: bool
    message: str | None = None
    id: str | None = None
    tenant_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
  

class CreateNotificationBannerSettingDto(BaseModel):
    is_enabled: bool
    message: str | None = None

class UpdateNotificationBannerSettingDto(CreateNotificationBannerSettingDto):
    pass

