from typing import Any

from beanie import PydanticObjectId
from api.common.base_repository import BaseRepository
from api.common.utils import get_logger
from api.domain.entities.user_preference import UserPreference

logger = get_logger(__name__)

class UserPreferenceRepository(BaseRepository[UserPreference]): 
    def __init__(self):
        super().__init__(UserPreference)

    async def get_preferences(self, user_id: str) -> UserPreference | None:
        user_pref = await self.single_or_none(user_id=PydanticObjectId(user_id))
        if user_pref is not None:
            return user_pref
        return None

    async def set_preferences(self, user_id: str, preferences: dict[str, Any]) -> None:
        existing = await self.single_or_none(user_id=PydanticObjectId(user_id))
        if existing is None:
            new_pref = UserPreference(
                user_id=PydanticObjectId(user_id),
                preferences=preferences
            )
            await self.create(data=new_pref.model_dump())
            return
        await self.update(id=PydanticObjectId(user_id), data={"preferences": preferences})