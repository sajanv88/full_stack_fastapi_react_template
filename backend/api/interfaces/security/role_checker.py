# Factory methods for common permission patterns
from typing import List
from api.domain.enum.permission import Permission
from api.domain.security.user_access_management import UserAccessManagement


def check_permissions_for_current_role(required_permissions: List[Permission], any_permission: bool = False, allow_self_access: bool = False) -> UserAccessManagement:
    """Returns a UserAccessManagement instance with the specified permissions. Any of the permissions can be satisfied if any_permission is True."""
    return UserAccessManagement(
        required_permissions=required_permissions,
        any_permission=any_permission,
        allow_self_access=allow_self_access
    )()



