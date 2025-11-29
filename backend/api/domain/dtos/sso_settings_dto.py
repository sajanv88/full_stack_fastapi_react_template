from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, field_serializer

from api.domain.entities.sso_settings import SSOProvider


class SSOSettingsDto(BaseModel):
    enabled: bool
    provider: SSOProvider
    client_id: str
    client_secret: Optional[str] | None = None

class CreateSSOSettingsDto(SSOSettingsDto):
    tenant_id: Optional[str] | None = None

class UpdateSSOSettingsDto(BaseModel):
    enabled: Optional[bool] | None = None
    provider: Optional[SSOProvider] | None = None
    client_id: Optional[str] | None = None
    client_secret: Optional[str] | None = None
    

class ReadSSOSettingsDto(SSOSettingsDto):
    id: str


class SSOSettingsListDto(BaseModel):
    items: list[ReadSSOSettingsDto]


class SSOSettingsResponseDto(BaseModel):
    message: str