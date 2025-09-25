from typing import Annotated, List
from fastapi import Depends
from api.common.exceptions import ForbiddenException
from api.common.utils import get_logger, is_tenancy_enabled
from api.core.container import get_role_service
from api.domain.dtos.user_dto import UserDto
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import get_current_user

logger = get_logger(__name__)

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

    async def get_role_detail(self, role_id: str):
    
        role_service = get_role_service()
        role = await role_service.get_role_by_id(role_id=role_id)
        return role

    async def check_self_access(self, current_user: UserDto, resource_id: str = None) -> bool:
        """Check if user is accessing their own resource"""
        if not resource_id or not self.allow_self_access:
            return False
        return current_user.id == resource_id
    
    async def has_permission(self, user_permissions: List[Permission], required_permissions: List[Permission]) -> bool:
        """Check if user has required permissions"""
        if self.any_permission:
            # User needs ANY of the required permissions
            return any(perm in user_permissions for perm in required_permissions)
        else:
            # User needs ALL of the required permissions
            return all(perm in user_permissions for perm in required_permissions)
    
    def __call__(self):
       
        async def check_permission(current_user: Annotated[UserDto, Depends(get_current_user)]) -> bool:

            resource_id = current_user.id
            logger.info(f"Resource ID for self-access checking: {resource_id}")

            if current_user.role_id is None:
                logger.info("User has no role assigned")
                raise ForbiddenException(f"No role assigned. Required. Please contact support.")
            
            role = await self.get_role_detail(current_user.role_id)
            user_permissions = role.permissions
            
            logger.info(f"User permissions: {[p.value if hasattr(p, 'value') else str(p) for p in user_permissions]}")
            logger.info(f"Required permissions: {[p.value if hasattr(p, 'value') else str(p) for p in self.required_permissions]}")

            if is_tenancy_enabled():
                if Permission.HOST_MANAGE_TENANTS in user_permissions:
                    logger.info("Host Permission detected - Granting all permissions")
                    return True


            # Check for full access (admin override)
            if Permission.FULL_ACCESS in user_permissions:
                logger.info("Full access granted - User has admin privileges")
                return True
            
            # Check for self-access permissions
            if (Permission.USER_SELF_READ_AND_WRITE_ONLY in user_permissions and 
                self.allow_self_access and resource_id):
                if await self.check_self_access(current_user, resource_id):
                    logger.info("Self access granted - User accessing own resource")
                    return True
            
            # Check required permissions
            if await self.has_permission(user_permissions, self.required_permissions):
                permission_type = "any" if self.any_permission else "all"
                logger.info(f"Access granted - User has {permission_type} required permissions")
                return True

            logger.error("Access denied - Insufficient permissions")
            raise ForbiddenException(f"Insufficient permissions. Required: {[p.value if hasattr(p, 'value') else str(p) for p in self.required_permissions]}")
        
        return check_permission
   
     
