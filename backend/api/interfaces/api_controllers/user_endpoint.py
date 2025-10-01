from fastapi import APIRouter, Depends, File, UploadFile, status
from api.common.exceptions import InvalidOperationException
from api.common.utils import get_logger
from api.domain.dtos.user_dto import CreateUserDto, CreateUserResponseDto, UpdateUserDto, UserDto, UserListDto, UserProfileImageUpdateDto, UserRoleUpdateRequestDto
from api.domain.enum.permission import Permission
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.file_service import FileService
from api.usecases.user_service import UserService
from api.core.container import get_file_service, get_user_service


logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=UserListDto)
async def list_users(
    skip: int = 0, limit: int = 10,
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

@router.get("/profile/{image_key:path}", response_model=UserProfileImageUpdateDto)
async def get_profile_image(
    image_key: str,
    file_service: FileService = Depends(get_file_service)
):
    image_url = await file_service.get_file_url(image_key)
    return UserProfileImageUpdateDto(image_url=image_url)

@router.delete("/{user_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
    _bool: bool = Depends(check_permissions_for_current_role(required_permissions=[Permission.USER_DELETE_ONLY]))
):
    await service.delete_user(user_id)
    return status.HTTP_202_ACCEPTED




@router.put("/{user_id}/update_profile_picture", response_model=UserProfileImageUpdateDto, status_code=status.HTTP_202_ACCEPTED)
async def update_profile_picture(
    user_id: str,
    file: UploadFile = File(...),
    _bool: bool = Depends(check_permissions_for_current_role(
        required_permissions=[Permission.USER_READ_AND_WRITE_ONLY, Permission.USER_SELF_READ_AND_WRITE_ONLY],
        allow_self_access=True)),
    user_service: UserService = Depends(get_user_service),
    file_service: FileService = Depends(get_file_service),
):
    await user_service.get_user_by_id(user_id)
    file_location = await file_service.upload_file(file)
    await user_service.update_user(user_id=user_id, user_data=UpdateUserDto(image_url=file_location))
    return UserProfileImageUpdateDto(image_url=file_location)


@router.patch("/{user_id}/assign_role", response_model=UserDto, status_code=status.HTTP_202_ACCEPTED)
async def patch_user(
    user_id: str, role_update: UserRoleUpdateRequestDto,
    _: bool = Depends(check_permissions_for_current_role([Permission.USER_ROLE_ASSIGN_OR_REMOVE_ONLY])),
    user_service: UserService = Depends(get_user_service)

):
    
    exsisting_user = await user_service.get_user_by_id(user_id)
    if str(exsisting_user.role_id) == role_update.role_id:
        raise InvalidOperationException("User already has this role assigned")
    
    user = await user_service.update_user(user_id=user_id, user_data=UpdateUserDto(role_id=role_update.role_id))
    user_doc = await user.to_serializable_dict()
    return UserDto(**user_doc)
  


@router.patch("/{user_id}/remove_role", response_model=UserDto, status_code=status.HTTP_202_ACCEPTED)
async def remove_user_role(
     user_id: str, role_update: UserRoleUpdateRequestDto,
    _: bool = Depends(check_permissions_for_current_role([Permission.USER_ROLE_ASSIGN_OR_REMOVE_ONLY])),
    user_service: UserService = Depends(get_user_service)
):
    exsisting_user = await user_service.get_user_by_id(user_id)
    if str(exsisting_user.role_id) != role_update.role_id:
        raise InvalidOperationException("User does not have this role assigned")
    
    user = await user_service.update_user(user_id=user_id, user_data=UpdateUserDto(role_id=None))
    user_doc = await user.to_serializable_dict()
    return UserDto(**user_doc)
