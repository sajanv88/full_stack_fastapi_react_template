from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class User(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    gender: Gender
    role_id: Optional[str] = None
    is_active: bool
    activated_at: Optional[datetime] = None
    created_at: datetime
    image_url: Optional[str] = None

class NewUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    gender: Gender
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[Gender] = None
    image_url: Optional[str] = None


class UserEmailUpdate(BaseModel):
    email: str
