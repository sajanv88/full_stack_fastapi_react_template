from pydantic import BaseModel
from enum import Enum


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

class NewUser(BaseModel):
    first_name: str
    last_name: str
    email: str
    gender: Gender