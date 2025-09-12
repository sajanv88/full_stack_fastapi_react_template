from pydantic import BaseModel


class UserPreference(BaseModel):
    user_id: str
    preferences: dict