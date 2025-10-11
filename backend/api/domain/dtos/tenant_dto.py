
from typing import  List, Literal, Optional
from pydantic import BaseModel, EmailStr

from api.common.enums.gender import Gender
from api.domain.entities.tenant import CustomDomain, Subdomain


class TenantDto(BaseModel):
    id: Optional[str]
    name: str
    subdomain: Optional[str] | None
    is_active: bool
    custom_domain: Optional[str] | None
    custom_domain_status: Literal["active", "failed", "activation-progress"] = "failed"

class CreateTenantDto(BaseModel):
    name: str
    subdomain: Subdomain
    admin_email: EmailStr
    admin_password: str
    first_name: str
    last_name: str
    gender: Gender

class TenantListDto(BaseModel):
    tenants: List[TenantDto]
    skip: int
    limit: int
    total: int
    hasPrevious: bool
    hasNext: bool


class CreateTenantResponseDto(BaseModel):
    id: str


class SubdomainAvailabilityDto(BaseModel):
    is_available: bool

class UpdateTenantDto(BaseModel):
    is_active: Optional[bool]
    custom_domain: Optional[CustomDomain] | None


class UpdateTenantResponseDto(BaseModel):
   message: str