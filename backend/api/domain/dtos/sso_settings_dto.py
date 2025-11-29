from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, field_serializer

from api.domain.entities.sso_settings import SSOProvider


class SSOSettingsDto(BaseModel):
    enabled: bool
    provider: SSOProvider
    client_id: str
    client_secret: str

class CreateSSOSettingsDto(SSOSettingsDto):
    tenant_id: Optional[str] | None = None

class UpdateSSOSettingsDto(BaseModel):
    enabled: Optional[bool] | None = None
    provider: Optional[SSOProvider] | None = None
    client_id: Optional[str] | None = None
    client_secret: Optional[str] | None = None
    

class ReadSSOSettingsDto(SSOSettingsDto):
    id: str
    @field_serializer("id")
    def serialize_id(self, v: PydanticObjectId) -> str:
        return str(v)

class SSOSettingsListDto(BaseModel):
    items: list[ReadSSOSettingsDto]


class SSOSettingsResponseDto(BaseModel):
    message: str