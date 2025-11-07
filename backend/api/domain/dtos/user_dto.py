from typing import  List, Optional
from pydantic import BaseModel, EmailStr
from beanie import PydanticObjectId
from api.common.enums.gender import Gender



class BaseUserDto(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    gender: Gender
    tenant_id: PydanticObjectId | None = None
    role_id: PydanticObjectId | None = None

class CreateUserDto(BaseUserDto):
    password: str
    sub_domain: Optional[str] = None


class UpdateUserDto(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    gender: Optional[Gender] = None
    image_url: Optional[str] = None
    role_id: Optional[str] = None
    is_active: Optional[bool] = None
    tenant_id: PydanticObjectId | None = None


class UserDto(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    gender: Gender
    role_id: Optional[str] = None
    is_active: bool
    activated_at: Optional[str] = None
    image_url: Optional[str] = None
    created_at: str
    updated_at: str
    tenant_id: Optional[str] = None


class UserListDto(BaseModel):
    users: List[UserDto]
    skip: int
    limit: int
    total: int
    has_previous: bool
    has_next: bool


class CreateUserResponseDto(BaseModel):
    id: str


class UserActivationRequestDto(BaseModel):
    token: str

class UserResendActivationEmailRequestDto(BaseModel):
    email: EmailStr
    id: str
    first_name: str
    tenant_id: Optional[str] = None 

class UserProfileImageUpdateDto(BaseModel):
    image_url: str


class UserRoleUpdateRequestDto(BaseModel):
    role_id: str

