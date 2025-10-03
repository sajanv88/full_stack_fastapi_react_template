from openai import BaseModel


class PermissionDto(BaseModel):
    name: str