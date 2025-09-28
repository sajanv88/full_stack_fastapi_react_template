
from pydantic import BaseModel, EmailStr


class PasswordResetRequestDto(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequestDto(BaseModel):
    new_password: str

class PasswordResetResponseDto(BaseModel):
    message: str

class ChangeEmailRequestDto(BaseModel):
    new_email: EmailStr