from typing import Annotated, List
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status
from api.common.exceptions import InvalidOperationException
from api.common.utils import get_logger
from api.domain.dtos.role_dto import CreateRoleDto, CreateRoleResponseDto, RoleDto, RoleListDto, UpdateRoleDto
from api.core.container import get_role_service, get_user_service
from api.domain.enum.permission import Permission
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.role_service import RoleService
from api.usecases.user_service import UserService


logger = get_logger(__name__)

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=RoleListDto)
async def list_roles(
    skip: int = 0, limit: int = 10,
    service: RoleService = Depends(get_role_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.ROLE_VIEW_ONLY]))

):
    logger.info(f"Listing roles with skip={skip}, limit={limit}")
    return await service.list_roles(skip=skip, limit=limit)

@router.get("/search_by_name", response_model=List[RoleDto])
async def search_role_by_name(
    name: str,
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.ROLE_VIEW_ONLY])),
    service: RoleService = Depends(get_role_service)
):
    roles = await service.search_role_by_name(name)
    return [RoleDto(**(await role.to_serializable_dict())) for role in roles]

@router.post("/", response_model=CreateRoleResponseDto, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: CreateRoleDto,
    service: RoleService = Depends(get_role_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.ROLE_READ_AND_WRITE_ONLY]))
):  
    new_user_id = await service.create_role(data)
    return CreateRoleResponseDto(id=str(new_user_id))


@router.get("/{role_id}", response_model=RoleDto)
async def get_role(
    role_id: str,
    service: RoleService = Depends(get_role_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.ROLE_VIEW_ONLY]))
):
    role = await service.get_role_by_id(role_id)
    role_doc = await role.to_serializable_dict()
    return RoleDto(**role_doc)


@router.put("/{role_id}", response_model=RoleDto, status_code=status.HTTP_200_OK)
async def update_role(
    role_id: str,
    data: UpdateRoleDto,
    service: RoleService = Depends(get_role_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.ROLE_READ_AND_WRITE_ONLY]))
):
    role_doc = await service.update_role(role_id=role_id, role_data=data)
    serialized_role = await role_doc.to_serializable_dict()
    return RoleDto(**serialized_role)


@router.delete("/{role_id:path}", status_code=status.HTTP_202_ACCEPTED, description="Deletes a role if it is not assigned to any users.")
async def delete_role(
    role_id: str,
    service: RoleService = Depends(get_role_service),
    user_service: UserService = Depends(get_user_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.ROLE_DELETE_ONLY]))
):
    users_role = await user_service.total_count(params={"role_id": role_id})
    logger.debug(f"Number of users with role {role_id}: {users_role}")
    if users_role > 0:
        logger.warning(f"Cannot delete role {role_id} as it is assigned to users.")
        raise InvalidOperationException(f"Cannot delete role {role_id} as it is assigned to users.")
    
    await service.delete_role(role_id)
    return status.HTTP_202_ACCEPTED


