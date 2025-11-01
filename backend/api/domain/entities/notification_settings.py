from datetime import datetime
from beanie import PydanticObjectId
from api.domain.entities.api_base_model import ApiBaseModel
from typing import Optional
from pydantic import field_serializer

class NotificationBannerSetting(ApiBaseModel):
    is_enabled: bool
    message: Optional[str] = None

    @field_serializer("id", "tenant_id", "created_at", "updated_at")
    def serialize_fields(value: PydanticObjectId | datetime | None) -> Optional[str]:
        if isinstance(value, PydanticObjectId):
            return str(value)
        if isinstance(value, datetime):
            return str(value)  
        return value
    
    class Settings:
        name = "notification_banner_settings"
        indexes = ["tenant_id"]
