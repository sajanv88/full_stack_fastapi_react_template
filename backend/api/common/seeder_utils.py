from typing import List

from pydantic import BaseModel, Field

from api.domain.enum.permission import Permission
from api.domain.enum.role import RoleType


class Role(BaseModel):
    name: RoleType
    description: str
    permissions: List[Permission] = Field(default_factory=list)

def get_seed_roles() -> List[Role]:
    """Returns a list of default roles to be seeded into the database for a new tenant."""
    roles = [
        Role(
            name=RoleType.ADMIN,
            description="Admin role can give full access to application. Can read, write and delete any resource.",
            permissions=[Permission.FULL_ACCESS, Permission.MANAGE_STORAGE_SETTINGS, Permission.MANAGE_TENANT_SETTINGS]
            ),
        Role(
            name=RoleType.USER,
            description="Regular user has read and update their own resources.",
            permissions=[Permission.USER_SELF_READ_AND_WRITE_ONLY, Permission.USER_VIEW_ONLY, Permission.ROLE_VIEW_ONLY]
        ),
        Role(
            name=RoleType.GUEST,
            description="Guest user has read only access to resources.",
            permissions=[Permission.USER_VIEW_ONLY, Permission.ROLE_VIEW_ONLY]
        )
    ]
    return roles