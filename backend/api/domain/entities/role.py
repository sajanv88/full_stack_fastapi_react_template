from typing import List, Optional
from api.domain.entities.api_base_model import ApiBaseModel
from api.domain.enum.permission import Permission
from beanie import Indexed

class Role(ApiBaseModel):
    name: str = Indexed(str, unique=True)
    description: Optional[str] | None
    permissions: List[Permission] = [Permission.USER_VIEW_ONLY, Permission.ROLE_VIEW_ONLY]

    async def to_serializable_dict(self):
        base_doc = await super().to_serializable_dict()
        return {
            **base_doc,
            "name": self.name,
            "description": self.description,
            "permissions": [perm.value for perm in self.permissions],
        }

    class Settings:
        name = "roles"
