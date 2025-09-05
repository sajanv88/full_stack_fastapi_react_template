from typing import List, Any
from fastapi import Depends, HTTPException, status
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.role import RoleType
from app.core.db import role_collection, user_collection
from app.schemas.role_schema import serialize_role_schema
from app.schemas.user_schema import seralize_user_schema
from bson import ObjectId
from app.core.permission import Permission




class RoleChecker:
    def __init__(self, allowed_roles: List[str], permission: List[Permission]) -> None:
        self.allowed_roles = allowed_roles
        self.permission = permission

    async def get_role_detail(self, role_id: str):
        role = await role_collection.find_one({"_id": ObjectId(role_id)})
        return serialize_role_schema(role)


    async def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        print("Current User in RoleChecker:", current_user)
        if current_user['role_id'] is not None:
            role = await self.get_role_detail(current_user['role_id'])

        # Admin can perform any action
        if role["name"] in self.allowed_roles and Permission.FULL_ACCESS in role["permissions"]:
            print("Admin access granted.")
            return True

        # User can perform role assignment or removal
        if role["name"] in self.allowed_roles and Permission.USER_ROLE_ASSIGN_OR_REMOVE_ONLY in role["permissions"]:
            print("User role assignment/removal access granted.")
            return True

        # User can perform self update
        if role["name"] in self.allowed_roles and Permission.USER_SELF_READ_AND_WRITE_ONLY in role["permissions"]:
            # Check if user is trying to access their own resource.
            if Permission.ROLE_READ_AND_WRITE_ONLY not in role["permissions"] or Permission.ROLE_DELETE_ONLY not in role["permissions"]:
                user = await user_collection.find_one({"_id": ObjectId(current_user['_id'])})
                if user is not None:
                    user_dict = seralize_user_schema(user)
                    if user_dict["id"] == str(current_user["_id"]):
                        return True
                    
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You do not have access to perform this action.")





# Admin only resource can perform any operation in user resource.
read_write_resource = RoleChecker(allowed_roles=[RoleType.ADMIN, RoleType.USER], permission=[Permission.FULL_ACCESS, Permission.USER_SELF_READ_AND_WRITE_ONLY])

# Currently Admin only can perform this operation
user_assign_or_remove_role_resource = RoleChecker(allowed_roles=[RoleType.ADMIN], permission=[Permission.USER_ROLE_ASSIGN_OR_REMOVE_ONLY])