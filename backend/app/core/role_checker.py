from typing import List, Any
from fastapi import Depends, HTTPException, status
from app.api.routes.auth import get_current_user
from app.models.user import User
from app.models.role import RoleType
from app.core.db import role_collection, user_collection
from app.schemas.role_schema import serialize_role_schema
from app.schemas.user_schema import seralize_user_schema
from bson import ObjectId

class RoleChecker:
    def __init__(self, allowed_roles: List[str], not_allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles
        self.not_allowed_roles = not_allowed_roles

    async def get_role_detail(self, role_id: str):
        role = await role_collection.find_one({"_id": ObjectId(role_id)})
        return serialize_role_schema(role)


    async def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        print("Current User in RoleChecker:", current_user)
        if current_user['role_id'] is not None:
            role = await self.get_role_detail(current_user['role_id'])

        if role["name"] in self.allowed_roles:
            return True
        
        if role["name"] in self.not_allowed_roles:
            user = await user_collection.find_one({"_id": ObjectId(current_user['_id'])})
            if user is not None:
                user_dict = seralize_user_schema(user)
                if user_dict["id"] == str(current_user["_id"]):
                    print("You can modify your account.")
                    return True
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You do not have access to perform this action.")
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You do not have access to perform this action.")


view_only_resource = RoleChecker(allowed_roles=[RoleType.GUEST, RoleType.ADMIN, RoleType.USER], not_allowed_roles=[])

# Admin only resource can perform any operation in user resource.
admin_only_user_resource = RoleChecker(allowed_roles=[RoleType.ADMIN], not_allowed_roles=[RoleType.USER, RoleType.GUEST])

# Admin only resource can perform any operation in role resource.
admin_only_role_resource = RoleChecker(allowed_roles=[RoleType.ADMIN], not_allowed_roles=[])
