from typing import List, Optional
from pydantic import BaseModel

from api.domain.dtos.ai_dto import AIModelInfoDto
from api.domain.dtos.user_preference_dto import UserPreferenceDto


class AppConfigurationDto(BaseModel):
    is_multi_tenant_enabled: bool
    multi_tenancy_strategy: str  # "subdomain" or "header"
    host_main_domain: str
    available_ai_models: Optional[List[AIModelInfoDto]] = []
    is_user_logged_in: Optional[bool] = False
    user_preferences: Optional[UserPreferenceDto] = None


