from typing import Optional
from pydantic import BaseModel

from api.domain.dtos.branding_dto import BrandingDto
from api.domain.dtos.tenant_dto import TenantDto
from api.domain.dtos.user_preference_dto import UserPreferenceDto


class AppConfigurationDto(BaseModel):
    is_multi_tenant_enabled: bool
    multi_tenancy_strategy: str  # "subdomain" or "header"
    host_main_domain: str
    is_user_logged_in: Optional[bool] = False
    user_preferences: Optional[UserPreferenceDto] = None
    current_tenant: TenantDto | None = None
    environment: str
    enabled_sso_providers: Optional[list[str]] = None
    branding: Optional[BrandingDto] = None


    

