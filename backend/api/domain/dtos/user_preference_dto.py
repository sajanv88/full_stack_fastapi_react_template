from typing import Any
from pydantic import BaseModel


class UserPreferenceDto(BaseModel):
    user_id: str
    preferences: dict[str, Any]

