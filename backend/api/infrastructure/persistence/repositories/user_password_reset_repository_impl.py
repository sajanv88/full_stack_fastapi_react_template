from api.common.base_repository import BaseRepository
from api.domain.entities.user_password_reset import UserPasswordReset
from beanie import PydanticObjectId
from api.common.utils import get_utc_now, get_logger
logger = get_logger(__name__)

class UserPasswordResetRepository(BaseRepository[UserPasswordReset]):
    def __init__(self):
        super().__init__(UserPasswordReset)

    async def set_password_reset(self, user_id: str) -> UserPasswordReset:
        existing = await self.single_or_none(user_id=user_id)
        token_secret = PydanticObjectId()
        if existing:
            existing.token_secret = str(token_secret)
            existing.reset_secret_updated_at = get_utc_now()
            logger.info(f"Updating password reset for user {user_id}")
            return await existing.save()
        new_reset = UserPasswordReset(
            user_id = user_id,
            token_secret = str(token_secret),
            reset_secret_updated_at = get_utc_now()
        )
        logger.info(f"Creating password reset for user {user_id}")
        return await self.create(data = new_reset.model_dump())
    

    async def delete_by_user_id(self, user_id: str) -> bool:
        existing = await self.single_or_none(user_id=user_id)
        if existing is None:
            logger.warning(f"Password reset not found for user {user_id}")
            return False
        await existing.delete()
        logger.info(f"Deleted password reset for user {user_id}")
        return True