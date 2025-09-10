from typing import Annotated, Any, List, Optional
from fastapi import Depends, HTTPException, status
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.core.db import get_db_reference, client
from app.core.permission import Permission
from app.core.utils import get_default_db_name, is_tenancy_enabled
from app.services.role_service import RoleService

class DynamicRoleChecker:
    def __init__(self,
        required_permissions: List[Permission],
        any_permission: bool = True,
        allow_self_access: bool = True
    ):
        """
        Initialize dynamic role checker
        
        Args:
            required_permissions: List of permissions required to access the resource
            any_permission: If True, user needs ANY of the permissions. If False, user needs ALL permissions
            allow_self_access: If True, allows self-access with USER_SELF_READ_AND_WRITE_ONLY permission
        """
        self.required_permissions = required_permissions
        self.any_permission = any_permission
        self.allow_self_access = allow_self_access

    async def get_role_detail(self, role_id: str, tenant_id: Optional[str] = None):
        db = client[get_default_db_name()]
        if tenant_id is not None and is_tenancy_enabled():
            db = client[f"tenant_{tenant_id}"]

        role_service = RoleService(db)
        role = await role_service.get_role(role_id)
        return role

    async def check_self_access(self, current_user: User, resource_id: str = None) -> bool:
        """Check if user is accessing their own resource"""
        if not resource_id or not self.allow_self_access:
            return False
        return str(current_user['_id']) == resource_id
    
    async def has_permission(self, user_permissions: List[Permission], required_permissions: List[Permission]) -> bool:
        """Check if user has required permissions"""
        if self.any_permission:
            # User needs ANY of the required permissions
            return any(perm in user_permissions for perm in required_permissions)
        else:
            # User needs ALL of the required permissions
            return all(perm in user_permissions for perm in required_permissions)
    
    def __call__(self):
       
        async def check_permission(current_user: Annotated[User, Depends(get_current_user)]) -> bool:
            print(f"Dynamic Role Checker - User: {current_user.get('email', 'unknown')}")

            resource_id = current_user.get('_id', None)
            print(f"Resource ID for self-access checking: {resource_id}")

            if current_user['role_id'] is None:
                print("User has no role assigned")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User has no role assigned"
                )
            
            role = await self.get_role_detail(current_user['role_id'], tenant_id=current_user.get('tenant_id'))
            user_permissions = role.get("permissions", [])
            
            print(f"User permissions: {[p.value if hasattr(p, 'value') else str(p) for p in user_permissions]}")
            print(f"Required permissions: {[p.value if hasattr(p, 'value') else str(p) for p in self.required_permissions]}")

            if is_tenancy_enabled():
                if Permission.HOST_MANAGE_TENANTS in user_permissions:
                    print("Host Permission detected - Granting all permissions")
                    return True


            # Check for full access (admin override)
            if Permission.FULL_ACCESS in user_permissions:
                print("Full access granted - User has admin privileges")
                return True
            
            # Check for self-access permissions
            if (Permission.USER_SELF_READ_AND_WRITE_ONLY in user_permissions and 
                self.allow_self_access and resource_id):
                if await self.check_self_access(current_user, resource_id):
                    print("Self access granted - User accessing own resource")
                    return True
            
            # Check required permissions
            if await self.has_permission(user_permissions, self.required_permissions):
                permission_type = "any" if self.any_permission else "all"
                print(f"Access granted - User has {permission_type} required permissions")
                return True
            
            print("Access denied - Insufficient permissions")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {[p.value if hasattr(p, 'value') else str(p) for p in self.required_permissions]}"
            )
        
        return check_permission
   
     
# Factory methods for common permission patterns
def create_permission_checker(permissions: List[Permission], any_permission: bool = False, allow_self_access: bool = False) -> DynamicRoleChecker:
    """Create a dynamic role checker with specific permissions"""
    return DynamicRoleChecker(
        required_permissions=permissions,
        any_permission=any_permission,
        allow_self_access=allow_self_access
    )()



