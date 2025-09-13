from datetime import datetime, timezone
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from bson import ObjectId
class AIHistoryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.chat_histories_collection: AsyncIOMotorCollection = db.chat_histories_ai

    async def get_user_history(self, user_id: str, limit: int = 100):
        history = await self.chat_histories_collection.find({"user_id": ObjectId(user_id)}).to_list(length=limit)
        return history

    async def save_user_query(self, user_id: str, query: str, response: str):
        await self.chat_histories_collection.insert_one({
            "user_id": ObjectId(user_id),
            "query": query,
            "response": response,
            "timestamp": datetime.now(timezone.utc)
        })
    
    async def get_single_history(self, history_id: str):
        history = await self.chat_histories_collection.find_one({"_id": ObjectId(history_id)})
        return await self.serialize(history) if history else None

    async def delete_history(self, history_id: str):
        result = await self.chat_histories_collection.delete_one({"_id": ObjectId(history_id)})
        return result.deleted_count > 0

    async def serialize(self, history: dict):
        return {
            "id": str(history["_id"]),
            "user_id": str(history["user_id"]),
            "query": history["query"],
            "response": history["response"],
            "timestamp": str(history["timestamp"].isoformat())
        }