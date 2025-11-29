from typing import Literal, Optional

from beanie import PydanticObjectId
from api.domain.entities.api_base_model import ApiBaseModel
from pydantic import field_serializer

type SSOProvider = Literal["google", "github", "discord", "microsoft", "linkedin", "x", "notion", "gitlab", "bitbucket", "facebook"]

class SSOSettings(ApiBaseModel):
    enabled: bool = False
    provider: Optional[SSOProvider] = None
    client_id: str | None = None
    client_secret: str | None = None

    @field_serializer("id")
    def serialize_id(self, v: PydanticObjectId) -> Optional[str]:
        return str(v) if v else None
    
    
    class Settings:
        name = "sso_settings"
        indexes = ["enabled", "provider", "tenant_id"]