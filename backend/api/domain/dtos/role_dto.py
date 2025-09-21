from typing import List, Optional
from beanie import PydanticObjectId
from pydantic import BaseModel

from api.domain.enum.permission import Permission


class RoleDto(BaseModel):
    id: str
    name: str
    description: Optional[str] | None
    permissions: List[Permission] = []
    created_at: str
    updated_at: str
    tenant_id: Optional[str] | None = None


class RoleListDto(BaseModel):
    roles: List[RoleDto]
    skip: int
    limit: int
    total: int
    hasPrevious: bool
    hasNext: bool

class CreateRoleDto(BaseModel):
    name: str
    description: Optional[str] | None = None
    tenant_id: PydanticObjectId | None = None

class UpdateRoleDto(CreateRoleDto):
    permissions: List[Permission] = []


class CreateRoleResponseDto(BaseModel):
    id: str


