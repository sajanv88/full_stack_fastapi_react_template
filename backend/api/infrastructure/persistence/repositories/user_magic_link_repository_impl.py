from beanie import PydanticObjectId
from api.common.base_repository import BaseRepository
from api.common.exceptions import ApiBaseException
from api.common.utils import get_logger
from api.domain.entities.user_magic_link import UserMagicLink

logger = get_logger(__name__)

class UserMagicLinkRepository(BaseRepository[UserMagicLink]):
    def __init__(self):
        super().__init__(UserMagicLink)
    
    async def create_magic_link(self, user_id: str, token: str) -> UserMagicLink:
        """
        Create a magic link for the given user ID with the provided token. Raises an exception if the user has exceeded the allowed number of magic link requests.
        Args:
            user_id (str): The ID of the user to create the magic link for.
            token (str): The token to associate with the magic link.
        Returns:
            UserMagicLink: The created UserMagicLink document.
        """
        count = await self.count({"user_id": PydanticObjectId(user_id)})
        logger.info(f"Magic link requests count for user {user_id}: {count}")    
        if count > 3:
            raise ApiBaseException("Too many magic link requests. Please try again later.")

        new_link = UserMagicLink(
            user_id=user_id,
            token=token
        )
        return await self.create(data=new_link.model_dump())
    
    