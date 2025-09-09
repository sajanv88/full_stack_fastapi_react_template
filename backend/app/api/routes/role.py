from datetime import datetime
from fastapi import Depends, APIRouter, status, HTTPException, Response
from pydantic import BaseModel
from typing import List
from app.models.user import  User
from app.models.role import NewRole, Role

from typing import Annotated
from app.api.routes.auth import get_current_user
from app.core.role_checker import  create_permission_checker
from app.core.permission import Permission
from app.services.role_service import RoleService
from app.core.db import get_db_reference


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
    skip: int = 0, limit: int = 10,
    _: bool = Depends(create_permission_checker([Permission.ROLE_VIEW_ONLY])),
     db = Depends(get_db_reference)
):
    role_service = RoleService(db)
    roles_data = await role_service.list_roles(skip=skip, limit=limit)
    total = await role_service.total_count()
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
    _: bool = Depends(create_permission_checker([Permission.ROLE_READ_AND_WRITE_ONLY])),
     db = Depends(get_db_reference)
):
    role_service = RoleService(db)
    try:
        result = await role_service.create_role({
            "name": role.name,
            "description": role.description,
            "permissions": [Permission.USER_VIEW_ONLY, Permission.ROLE_VIEW_ONLY],  # Default permissions
            "created_at": datetime.utcnow()
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
    _: bool = Depends(create_permission_checker([Permission.ROLE_VIEW_ONLY])),
    db = Depends(get_db_reference)
):
    role_service = RoleService(db)
    role = await role_service.get_role(role_id)
    if role:
        return role
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")


@router.delete("/{role_id}", response_class=Response)
async def delete_role(
    current_user: Annotated[User, Depends(get_current_user)],
    role_id: str,
    _: bool = Depends(create_permission_checker([Permission.ROLE_DELETE_ONLY])),
    db = Depends(get_db_reference)
):
    role_service = RoleService(db)
    result = await role_service.delete_role(role_id)
    if result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    

@router.put("/{role_id}", response_model=Role)
async def update_role(
    current_user: Annotated[User, Depends(get_current_user)],
    role_id: str,
    role:  NewRole,
    _: bool = Depends(create_permission_checker([Permission.ROLE_READ_AND_WRITE_ONLY])),
    db = Depends(get_db_reference)
):
    role_service = RoleService(db)
    update_data = {k: v for k, v in role.model_dump().items() if v is not None}
    print("Updating role:", role_id, "with data:", update_data)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No data provided for update")

    result = await role_service.update_role(role_id, update_data)

    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    return await role_service.get_role(role_id)
    