from typing import Any

from beanie import PydanticObjectId
from api.domain.entities.api_base_model import ApiBaseModel


class UserPreference(ApiBaseModel):
    user_id: PydanticObjectId
    preferences: dict[str, Any]

    async def to_serializable_dict(self):
        base_doc = await super().to_serializable_dict()
        return {
            **base_doc,
            "user_id": str(self.user_id),
            "preferences": self.preferences or {},
        }

    class Settings:
        name = "user_preferences"
