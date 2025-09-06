from datetime import datetime
from pydantic import BaseModel
from typing import Union
from enum import Enum
from app.core.permission import Permission



# Default Role types
class RoleType(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class Role(BaseModel):
    id: str
    name: str
    description: Union[str, None] = None
    permissions: Union[list[Permission], None] = []
    created_at: datetime

class NewRole(BaseModel):
    name: str
    description: Union[str, None] = None
