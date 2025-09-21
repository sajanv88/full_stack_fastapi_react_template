from fastapi import APIRouter, Depends, status
from api.common.utils import get_logger
from api.domain.dtos.role_dto import CreateRoleDto, CreateRoleResponseDto, RoleDto, RoleListDto, UpdateRoleDto
from api.core.container import get_role_service
from api.usecases.role_service import RoleService


logger = get_logger(__name__)

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=RoleListDto)
async def list_roles(
    skip: int = 0, limit: int = 10,
    service: RoleService = Depends(get_role_service)
):
    logger.info(f"Listing roles with skip={skip}, limit={limit}")
    return await service.list_roles(skip=skip, limit=limit)


@router.post("/", response_model=CreateRoleResponseDto, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: CreateRoleDto,
    service: RoleService = Depends(get_role_service),
):  
    new_user_id = await service.create_role(data)
    return CreateRoleResponseDto(id=str(new_user_id))


@router.get("/{role_id}", response_model=RoleDto)
async def get_role(role_id: str, service: RoleService = Depends(get_role_service)):
    role = await service.get_role_by_id(role_id)
    role_doc = await role.to_serializable_dict()
    return RoleDto(**role_doc)


@router.put("/{role_id}", response_model=RoleDto, status_code=status.HTTP_200_OK)
async def update_role(
    role_id: str,
    data: UpdateRoleDto,
    service: RoleService = Depends(get_role_service),
):
    role_doc = await service.update_role(role_id=role_id, role_data=data)
    serialized_role = await role_doc.to_serializable_dict()
    return RoleDto(**serialized_role)


@router.delete("/{role_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_role(role_id: str, service: RoleService = Depends(get_role_service)):
    await service.delete_role(role_id)
    return status.HTTP_202_ACCEPTED


