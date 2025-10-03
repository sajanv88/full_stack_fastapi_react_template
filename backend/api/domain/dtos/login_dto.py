from pydantic import BaseModel, EmailStr


class LoginRequestDto(BaseModel):
    email: EmailStr
    password: str
