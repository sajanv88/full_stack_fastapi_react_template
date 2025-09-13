from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
import logging

from app.models.user_perference import UserPreference
from app.services.users_service import UserService


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
        logger.debug(f"Preferences found for user_id {user_id}: {preference}")
        return await self.serialize(preference)
    
    async def save(self, user_id:str, perferences: dict):
        user_service = UserService(self.db)
        await user_service.get_user(user_id)
        result = await self.user_preference_collection.update_one(
                {"user_id": ObjectId(user_id)},
                {"$set": {"preferences": perferences}},
                upsert=True
            )
        return result

    async def serialize(self, preference: dict):
        return  {
            "id": str(preference["_id"]),
            "user_id": str(preference["user_id"]),
            "preferences": preference.get("preferences", {})
        }

        