from datetime import datetime
from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, Field, field_serializer

from api.domain.entities.branding import ContactInfo, LogoType, ThemeConfig


class BrandingDto(BaseModel):
    id: str
    logo_type: Optional[LogoType] = None
    contact_info: Optional[ContactInfo] = None
    theme_config: ThemeConfig = Field(default_factory=ThemeConfig)
    tenant_id: str
    created_at: str
    updated_at: str
    app_name: str = "SaaS Org"
    favicon_url: Optional[str] = None
    logo_url: Optional[str] = None

   
    

class UpdateBrandingDto(BaseModel):
    contact_info: Optional[ContactInfo] = None
    theme_config: Optional[ThemeConfig] = None
    tenant_id: Optional[str] = None