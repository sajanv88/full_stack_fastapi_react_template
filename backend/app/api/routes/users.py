import logging
from datetime import datetime
from fastapi import BackgroundTasks, Depends, APIRouter, File, UploadFile, status, HTTPException, Response, Form
from pydantic import BaseModel
from typing import List
from app.core.db import get_db_reference
from app.models.user import NewUser, User, UserUpdate
from bson import ObjectId
from typing import Annotated
from app.api.routes.auth import get_current_user
from app.core.smtp_email import send_activation_email, ActivationEmailSchema
from app.core.password import get_password_hash
from app.core.role_checker import  create_permission_checker
from app.core.permission import Permission
from app.models.role import RoleType
from app.services.storage_service import StorageService
from app.services.users_service import UserService
from app.core.utils import save_file
from app.services.role_service import RoleService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users")
router.tags = ["Users"]


class UserListData(BaseModel):
    users: List[User]
    skip: int
    limit: int
    total: int
    hasPrevious: bool
    hasNext: bool

class UserListResponse(BaseModel):
    status: int
    message: str
    data: UserListData

class UserRoleUpdateRequest(BaseModel):
    role_id: str

class ProfileImageUpdateResponse(BaseModel):
    image_url: str


@router.get("/", response_model=UserListResponse)
async def get_users(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0, limit: int = 10,
    _: bool = Depends(create_permission_checker([Permission.USER_VIEW_ONLY])),
    db = Depends(get_db_reference)
):
    user_service = UserService(db)
    users_data = await user_service.list_users(skip=skip, limit=limit)
    total = await user_service.total_count()
    hasPrevious = skip > 0
    hasNext = (skip + limit) < total
    
    data = UserListData(
        users=users_data,
        skip=skip,
        limit=limit,
        total=total,
        hasPrevious=hasPrevious,
        hasNext=hasNext
    )
    
    return UserListResponse(
        status=status.HTTP_200_OK,
        message="Users retrieved successfully",
        data=data
    )
    

@router.post("/",  response_class=Response)
async def create_user(
    current_user: Annotated[User, Depends(get_current_user)],
    background_tasks: BackgroundTasks,
    user: NewUser,
    _: bool = Depends(create_permission_checker([Permission.USER_READ_AND_WRITE_ONLY])),
    db = Depends(get_db_reference)
):
    try:
        # Hash the password
        hashed_password = get_password_hash(user.password)

        role_service = RoleService(db)
        role_guest = await role_service.find_by_name(RoleType.GUEST)

        # Create user document
        user_doc = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "gender": user.gender.value,
            "password": hashed_password,
            "role_id": ObjectId(role_guest["_id"]),
            "created_at": datetime.utcnow(),
            
            "is_active": False  # User starts as inactive until activation
        }
        user_service = UserService(db)
        result = await user_service.create_user(user_doc)
        logger.info(f"User created with ID: {result.inserted_id}")
        if result.inserted_id:
            # Send activation email
            activation_email_data = ActivationEmailSchema(
                email=user.email,
                user_id=str(result.inserted_id),
                first_name=user.first_name
            )
            background_tasks.add_task(send_activation_email, activation_email_data)

        return Response(status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating user"
        )


@router.get("/{user_id}", response_model=User)
async def get_user(
    current_user: Annotated[User, Depends(get_current_user)],
    user_id: str,
    _: bool = Depends(create_permission_checker([
        Permission.USER_VIEW_ONLY, 
        Permission.USER_SELF_READ_AND_WRITE_ONLY
    ])),
     db = Depends(get_db_reference)
):
    try:
        user_service = UserService(db)
        user = await user_service.get_user(user_id)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{user_id}", response_class=Response)
async def delete_user(
    current_user: Annotated[User, Depends(get_current_user)],
    user_id: str,
    _: bool = Depends(create_permission_checker([Permission.FULL_ACCESS, Permission.USER_DELETE_ONLY])),
    db = Depends(get_db_reference)
):

    user_service = UserService(db)
    result = await user_service.delete_user(user_id)
    if result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@router.put("/{user_id}", response_model=User)
async def update_user(
    current_user: Annotated[User, Depends(get_current_user)],
    user: UserUpdate,
    user_id: str,
    _: bool = Depends(create_permission_checker([Permission.USER_SELF_READ_AND_WRITE_ONLY],any_permission=False, allow_self_access=True)),
    db = Depends(get_db_reference)
):
    user_service = UserService(db)
    exsiting_user = await user_service.get_user(user_id)

    if not exsiting_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    result = await user_service.update_user(user_id, {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "gender": user.gender.value
    })
    
    if result.modified_count == 1:
        return await user_service.get_user(user_id)
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found or no changes made"
    )

@router.put("/{user_id}/update_profile_picture", response_model=ProfileImageUpdateResponse)
async def update_profile_picture(
    current_user: Annotated[User, Depends(get_current_user)],
    user_id: str,
    file: UploadFile = File(...),
    _: bool = Depends(create_permission_checker([Permission.USER_SELF_READ_AND_WRITE_ONLY])),
    db = Depends(get_db_reference)
):
    user_service = UserService(db)
    existing_user = await user_service.get_user(user_id)

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Process the uploaded file and update the user's profile picture
    storage_service = StorageService(db)
    file_location = await storage_service.upload_file(file)

    result = await user_service.update_user(user_id, {"image_url": file_location})

    if result.modified_count == 1:
        return ProfileImageUpdateResponse(image_url=file_location)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found or no changes made"
    )


@router.patch("/{user_id}/assign_role", response_model=User)
async def patch_user(
    current_user: Annotated[User, Depends(get_current_user)],
    user_id: str, role_update: UserRoleUpdateRequest,
    _: bool = Depends(create_permission_checker([Permission.USER_ROLE_ASSIGN_OR_REMOVE_ONLY])),
    db = Depends(get_db_reference)

):
    try:
        user_service = UserService(db)
        user = await user_service.get_user(user_id)

        if "role_id" in user and user["role_id"] == ObjectId(role_update.role_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already has this role assigned")

        result = await user_service.assign_role(user_id, role_update.role_id)

        if result.modified_count == 1:
            return await user_service.get_user(user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or no changes made")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch("/{user_id}/remove_role", response_model=User)
async def remove_user_role(
    current_user: Annotated[User, Depends(get_current_user)],
    user_id: str,
    role_update: UserRoleUpdateRequest,
    _: bool = Depends(create_permission_checker([Permission.USER_ROLE_ASSIGN_OR_REMOVE_ONLY])),
    db = Depends(get_db_reference)
):
    try:
        user_service = UserService(db)
        user = await user_service.get_user(user_id)
    
        if "role_id" in user and user["role_id"] == ObjectId(role_update.role_id):
            await user_service.remove_role(user_id)
        
        return await user_service.get_user(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

