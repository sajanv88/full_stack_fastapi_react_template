from typing import List

from api.domain.enum.permission import Permission
from api.domain.enum.role import RoleType



def get_seed_roles() -> List[dict[str, any]]:
    """Returns a list of default roles to be seeded into the database for a new tenant."""
    roles = [
        {"name": RoleType.ADMIN, "description": "Admin role can give full access to application. Can read, write and delete any resource.", "permissions": [Permission.FULL_ACCESS, Permission.MANAGE_STORAGE_SETTINGS]},
        {"name": RoleType.USER, "description": "Regular user has read and update their own resources.", "permissions": [Permission.USER_SELF_READ_AND_WRITE_ONLY, Permission.USER_VIEW_ONLY, Permission.ROLE_VIEW_ONLY]},
        {"name": RoleType.GUEST, "description": "Guest user has read only access to resources.", "permissions": [Permission.USER_VIEW_ONLY, Permission.ROLE_VIEW_ONLY]}
    ]
    return roles