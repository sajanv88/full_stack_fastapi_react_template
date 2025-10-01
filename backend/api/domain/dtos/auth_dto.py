
from pydantic import BaseModel, EmailStr

from api.domain.dtos.role_dto import RoleDto
from api.domain.dtos.user_dto import UserDto


class PasswordResetRequestDto(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequestDto(BaseModel):
    new_password: str

class PasswordResetResponseDto(BaseModel):
    message: str

class ChangeEmailRequestDto(BaseModel):
    new_email: EmailStr

class ChangeEmailConfirmRequestDto(BaseModel):
    token: str

class ChangeEmailResponseDto(BaseModel):
    message: str

class MeResponseDto(UserDto):
    role: RoleDto