from fastapi import Depends, APIRouter, status, HTTPException, Response
from pydantic import BaseModel
from typing import List
from app.core.db import role_collection
from app.models.user import  User
from app.models.role import NewRole, Role
from app.schemas.role_schema import list_roles, serialize_role_schema
from bson import ObjectId
from typing import Annotated
from app.api.routes.auth import get_current_user
from app.core.role_checker import admin_only_role_resource, view_only_resource

router = APIRouter(prefix="/roles")
router.tags = ["Roles"]

class RoleListData(BaseModel):
    roles: List[Role]
    skip: int
    limit: int
    total: int
    hasPrevious: bool
    hasNext: bool

class RoleListResponse(BaseModel):
    status: int
    message: str
    data: RoleListData


@router.get("/", response_model=RoleListResponse)
async def get_roles(
    current_user: Annotated[User, Depends(get_current_user)],
    _:bool = Depends(view_only_resource),  
    skip: int = 0, limit: int = 10
):
    roles_cursor = role_collection.find().skip(skip).limit(limit)
    roles_data = list_roles(await roles_cursor.to_list(length=limit))
    total = await role_collection.count_documents({})
    hasPrevious = skip > 0
    hasNext = (skip + limit) < total
    
    data = RoleListData(
        roles=roles_data,
        skip=skip,
        limit=limit,
        total=total,
        hasPrevious=hasPrevious,
        hasNext=hasNext
    )
    
    return RoleListResponse(
        status=status.HTTP_200_OK,
        message="Roles retrieved successfully",
        data=data
    )


@router.post("/",  response_class=Response)
async def create_role(
    current_user: Annotated[User, Depends(get_current_user)],
    role: NewRole,
    _: bool = Depends(admin_only_role_resource)
):
    try:
        result = await role_collection.insert_one({
            "name": role.name,
            "description": role.description
        })
        if result.inserted_id:
            return Response(status_code=status.HTTP_201_CREATED)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role creation failed")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{role_id}", response_model=Role)
async def get_role( 
    current_user: Annotated[User, Depends(get_current_user)],
    role_id: str,
    _:bool = Depends(view_only_resource)

):
    role = await role_collection.find_one({"_id": ObjectId(role_id)})
    if role:
        return serialize_role_schema(role)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")


@router.delete("/{role_id}", response_class=Response)
async def delete_role(
    current_user: Annotated[User, Depends(get_current_user)],
    role_id: str,
    _: bool = Depends(admin_only_role_resource)

):
    result = await role_collection.delete_one({"_id": ObjectId(role_id)})
    if result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    

@router.put("/{role_id}", response_model=Role)
async def update_role(
    current_user: Annotated[User, Depends(get_current_user)],
    role_id: str,
    role:  NewRole,
    _: bool = Depends(admin_only_role_resource)
):
    update_data = {k: v for k, v in role.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided for update")
    
    result = await role_collection.update_one(
        {"_id": ObjectId(role_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    updated_role = await role_collection.find_one({"_id": ObjectId(role_id)})
    return serialize_role_schema(updated_role)