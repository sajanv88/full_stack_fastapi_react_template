from typing import List
from fastapi import Request
from api.common.exceptions import ForbiddenException
from api.common.utils import get_logger, is_tenancy_enabled
from api.domain.dtos.auth_dto import MeResponseDto
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import CurrentUser

logger = get_logger(__name__)

HOST_PERMISSIONS = {Permission.HOST_MANAGE_TENANTS}


def is_host_user(current_user: MeResponseDto) -> bool:
    """Host permissions only count outside of a tenant, a tenant role can never act on the host."""
    return (
        is_tenancy_enabled()
        and not current_user.tenant_id
        and Permission.HOST_MANAGE_TENANTS in current_user.role.permissions
    )


def has_any_permission(current_user: MeResponseDto, permissions: List[Permission]) -> bool:
    """True for host users, full access users, or users holding any of the given permissions."""
    user_permissions = current_user.role.permissions
    if is_host_user(current_user) or Permission.FULL_ACCESS in user_permissions:
        return True
    return any(permission in user_permissions for permission in permissions)


class UserAccessManagement:
    def __init__(self,
        required_permissions: List[Permission],
        any_permission: bool = True,
        allow_self_access: bool = True
    ):
        """
        Initialize user access management

        Args:
            required_permissions: List of permissions required to access the resource
            any_permission: If True, user needs ANY of the permissions. If False, user needs ALL permissions
            allow_self_access: If True, allows self-access with USER_SELF_READ_AND_WRITE_ONLY permission
        """
        self.required_permissions = required_permissions
        self.any_permission = any_permission
        self.allow_self_access = allow_self_access

    def is_self_access(self, current_user: MeResponseDto, target_user_id: str | None) -> bool:
        """Check if the user is accessing their own resource, as named by the {user_id} path parameter."""
        return (
            self.allow_self_access
            and target_user_id == current_user.id
            and Permission.USER_SELF_READ_AND_WRITE_ONLY in current_user.role.permissions
        )

    async def has_permission(self, user_permissions: List[Permission], required_permissions: List[Permission]) -> bool:
        """Check if user has required permissions"""
        if self.any_permission:
            # User needs ANY of the required permissions
            return any(perm in user_permissions for perm in required_permissions)
        else:
            # User needs ALL of the required permissions
            return all(perm in user_permissions for perm in required_permissions)

    def __call__(self):

        async def check_permission(request: Request, current_user: CurrentUser) -> bool:

            if current_user.role_id is None:
                logger.info("User has no role assigned")
                raise ForbiddenException(f"No role assigned. Required. Please contact support.")

            user_permissions = current_user.role.permissions

            logger.debug(f"User permissions: {[p.value for p in user_permissions]}")
            logger.debug(f"Required permissions: {[p.value for p in self.required_permissions]}")

            if is_host_user(current_user):
                logger.debug("Host Permission detected - Granting all permissions")
                return True

            # Tenant users can never satisfy a host permission, not even through full access.
            grantable = [p for p in self.required_permissions if not (current_user.tenant_id and p in HOST_PERMISSIONS)]

            # Check for full access (admin override)
            if grantable and Permission.FULL_ACCESS in user_permissions:
                logger.debug("Full access granted - User has admin privileges")
                return True

            # Check for self-access permissions
            if self.is_self_access(current_user, request.path_params.get("user_id")):
                logger.debug("Self access granted - User accessing own resource")
                return True

            # Holding the self permission only grants access to your own resource, handled above.
            checked = [p for p in grantable if p != Permission.USER_SELF_READ_AND_WRITE_ONLY]
            if checked and await self.has_permission(user_permissions, checked):
                permission_type = "any" if self.any_permission else "all"
                logger.debug(f"Access granted - User has {permission_type} required permissions")
                return True

            logger.error("Access denied - Insufficient permissions")
            raise ForbiddenException(f"Insufficient permissions. Required: {[p.value for p in self.required_permissions]}")

        return check_permission
