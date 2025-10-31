from datetime import datetime
from typing import Optional
from beanie import Indexed, PydanticObjectId
from pydantic import EmailStr
from api.common.enums.gender import Gender
from api.domain.entities.api_base_model import ApiBaseModel


class User(ApiBaseModel):
    first_name: str
    last_name: str
    email: EmailStr = Indexed(EmailStr, unique=True)
    gender: Gender = Indexed(str)
    role_id: Optional[PydanticObjectId] = None
    is_active: bool
    activated_at: Optional[datetime] = None
    image_url: Optional[str] = None
    password: str  # hashed password

    async def to_serializable_dict(self):
        base_doc = await super().to_serializable_dict()
        return {
            **base_doc,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "gender": str(self.gender.value),
            "role_id": str(self.role_id) if self.role_id else None,
            "is_active": self.is_active,
            "activated_at": str(self.activated_at) if self.activated_at else None,
            "image_url": str(self.image_url) if self.image_url else None,
        }
    

    class Settings:
        name = "users"
        indexes = [
            "email",
            "role_id",
            "is_active",
        ]