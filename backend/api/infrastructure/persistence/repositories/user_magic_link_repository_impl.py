from beanie import PydanticObjectId
from api.common.base_repository import BaseRepository
from api.common.exceptions import ApiBaseException
from api.common.utils import get_logger
from api.domain.entities.user_magic_link import UserMagicLink
from uuid import uuid4

logger = get_logger(__name__)

class UserMagicLinkRepository(BaseRepository[UserMagicLink]):
    def __init__(self):
        super().__init__(UserMagicLink)
    
    async def create_magic_link(self, user_id: str) -> UserMagicLink:
        count = await self.count({"user_id": PydanticObjectId(user_id)})
        logger.info(f"Magic link requests count for user {user_id}: {count}")    
        if count > 3:
            raise ApiBaseException("Too many magic link requests. Please try again later.")

        new_link = UserMagicLink(
            user_id=user_id,
            token=str(uuid4())
        )
        return await self.create(data=new_link.model_dump())
        