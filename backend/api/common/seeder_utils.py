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
            permissions=[Permission.FULL_ACCESS]
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
        ),
        Role(
            name=RoleType.BILLING_MANAGER,
            description="Billing manager can manage billing, payments settings, products and pricing.",
            permissions=[Permission.MANAGE_BILLING, Permission.MANAGE_PAYMENTS_SETTINGS, Permission.MANAGE_PRODUCTS_AND_PRICING]
        )
    ]
    return roles