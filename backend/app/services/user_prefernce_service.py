from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
import logging

from app.models.user_perference import UserPreference


logger = logging.getLogger(__name__)

class UserPreferenceService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.user_preference_collection: AsyncIOMotorCollection = db.user_preferences

    async def get_user_preference(self, user_id: str):
        preference = await self.user_preference_collection.find_one({"user_id": ObjectId(user_id)})
        if preference is None:
            logger.debug(f"No preferences found for user_id: {user_id}")
            return None
        return UserPreference(**preference)