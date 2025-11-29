from typing import Literal, Optional
from api.domain.entities.api_base_model import ApiBaseModel


type SSOProvider = Literal["google", "github", "discord", "microsoft", "linkedin", "x", "notion", "gitlab", "bitbucket", "facebook"]

class SSOSettings(ApiBaseModel):
    enabled: bool = False
    provider: Optional[SSOProvider] = None
    client_id: str | None = None
    client_secret: str | None = None

    class Settings:
        name = "sso_settings"
        indexes = ["enabled", "provider", "tenant_id"]