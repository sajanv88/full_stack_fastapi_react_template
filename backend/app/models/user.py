from pydantic import BaseModel

class Gender(str):
    male = "male"
    female = "female"
    other = "other"

class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    gender: Gender