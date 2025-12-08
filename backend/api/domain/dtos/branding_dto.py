from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, Field, field_serializer

from api.domain.entities.branding import ContactInfo, LogoType, ThemeConfig


class BrandingDto(BaseModel):
    id: str
    logo_type: LogoType
    contact_info: Optional[ContactInfo] = None
    theme_config: ThemeConfig = Field(default_factory=ThemeConfig)
    tenant_id: str
    created_at: str
    updated_at: str

    @field_serializer("id", "created_at", "updated_at", "tenant_id")
    def serialize_id(self, id: PydanticObjectId) -> str:
        return str(id)
    

class UpdateBrandingDto(BaseModel):
    contact_info: Optional[ContactInfo] = None
    theme_config: Optional[ThemeConfig] = None
    tenant_id: Optional[str] = None