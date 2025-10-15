from typing import Literal, Optional

from beanie import PydanticObjectId
from api.common.base_repository import BaseRepository
from api.domain.entities.user_passkey import Challenges, UserPasskey
import base64

class UserPasskeyRepository(BaseRepository[UserPasskey]):
    def __init__(self):
        super().__init__(UserPasskey)


class UserPasskeyChallengesRepository(BaseRepository[Challenges]):
    def __init__(self):
        super().__init__(Challenges)

    async def save_challenge(self, email: str, challenge: bytes, type: Literal["registration", "authentication"], tenant_id: Optional[PydanticObjectId] = None) -> Challenges:
        """
            Save challenges with current user email, return challenge
        """
        data = Challenges(
            email=email,
            challenge=base64.urlsafe_b64encode(challenge).decode(),
            type=type,
            tenant_id=tenant_id
        )
        return await self.create(data=data.model_dump())
    
    async def get_challenge(self, email: str, type: Literal["registration", "authentication"]) -> Optional[Challenges]:
        """
            Returns current challenge for the given email if found otherwise, None
        """
        return await self.single_or_none(email=email, type=type)
    

    async def delete_challenge(self, email: str, type: Literal["registration", "authentication"]) -> bool:
        """
            Delete the current challenge for the given email, Returns False if its not found, Otherwise, True
        """
        existing = await self.get_challenge(email=email, type=type)
        if existing is None:
            return False
        await existing.delete()
        return True

