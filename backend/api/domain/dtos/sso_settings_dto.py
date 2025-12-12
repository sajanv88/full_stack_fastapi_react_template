from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, field_serializer

from api.domain.entities.sso_settings import SSOProvider


class SSOSettingsDto(BaseModel):
    enabled: bool
    provider: SSOProvider
    client_id: str
    client_secret: Optional[str] | None = None
    scopes: Optional[list[str]] = []
    redirect_uris: Optional[list[str]] = []

class CreateSSOSettingsDto(SSOSettingsDto):
    tenant_id: Optional[str] | None = None

class UpdateSSOSettingsDto(BaseModel):
    enabled: Optional[bool] | None = None
    provider: Optional[SSOProvider] | None = None
    client_id: Optional[str] | None = None
    client_secret: Optional[str] | None = None
    scopes: Optional[list[str]] = None

class ReadSSOSettingsDto(SSOSettingsDto):
    id: str
    @field_serializer("client_secret")
    def mask_sensitive_fields(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if len(value) <= 4:
            return "*" * len(value)
        return value[:2] + "*" * (len(value) - 4) + value[-2:]

    @field_serializer("client_id")
    def mask_client_id(self, value: str) -> str:
        if len(value) <= 4:
            return "*" * len(value)
        return value[:2] + "*" * (len(value) - 4) + value[-2:]

class SSOSettingsListDto(BaseModel):
    items: list[ReadSSOSettingsDto]


class SSOSettingsResponseDto(BaseModel):
    message: str