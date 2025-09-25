from fastapi import APIRouter, Depends, Request, status
from typing import List
from api.common.utils import get_logger
from api.domain.dtos.user_dto import CreateUserDto, CreateUserResponseDto, UpdateUserDto, UserDto, UserListDto
from api.domain.enum.permission import Permission
from api.infrastructure.security.current_user import get_current_user
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.user_service import UserService
from api.core.container import get_user_service


logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=UserListDto)
async def list_users(
    skip: int = 0, limit: int = 10,
    current_user: UserDto = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.USER_VIEW_ONLY]))
):
    return await service.list_users(skip=skip, limit=limit)


@router.post("/", response_model=CreateUserResponseDto, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: CreateUserDto,
    service: UserService = Depends(get_user_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.USER_READ_AND_WRITE_ONLY]))
):

    new_user_id = await service.create_user(data)
    return CreateUserResponseDto(id=str(new_user_id))


@router.get("/{user_id}", response_model=UserDto)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
    _bool: bool = Depends(check_permissions_for_current_role(
        required_permissions=[Permission.USER_SELF_READ_AND_WRITE_ONLY],
        allow_self_access=True)
    )
):
    user = await service.get_user_by_id(user_id)
    user_doc = await user.to_serializable_dict()
    return UserDto(**user_doc)


@router.put("/{user_id}", response_model=UserDto, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: str,
    data: UpdateUserDto,
    service: UserService = Depends(get_user_service),
    _bool: bool = Depends(check_permissions_for_current_role(
        required_permissions=[Permission.USER_READ_AND_WRITE_ONLY, Permission.USER_SELF_READ_AND_WRITE_ONLY],
        allow_self_access=True)
    )

):
    user_doc = await service.update_user(user_id=user_id, user_data=data)
    serialized_user = await user_doc.to_serializable_dict()
    return UserDto(**serialized_user)


@router.delete("/{user_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.USER_DELETE_ONLY]))
):
    await service.delete_user(user_id)
    return status.HTTP_202_ACCEPTED

   


