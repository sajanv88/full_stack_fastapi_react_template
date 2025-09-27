from typing import Optional
from pydantic import BaseModel, EmailStr


class ActivationEmailSchemaDto(BaseModel):
    email: EmailStr
    user_id: str
    first_name: str
    tenant_id: Optional[str] = None
    jwt_secret: Optional[str] = None  # Used for password reset tokens

