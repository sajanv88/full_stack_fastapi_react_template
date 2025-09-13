import logging
from datetime import datetime, timezone
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from bson import ObjectId


logger = logging.getLogger(__name__)
class AIHistoryService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.chat_histories_collection: AsyncIOMotorCollection = db.chat_histories_ai
        self.chat_unique_sessions_collection: AsyncIOMotorCollection = db.chat_unique_sessions_ai

    async def get_user_history(self, user_id: str, limit: int = 100):
        history = await self.chat_histories_collection.find({"user_id": ObjectId(user_id)}).to_list(length=limit)
        return history

    async def is_session_exists(self, session_id: str) -> bool:
        session = await self.chat_unique_sessions_collection.find_one({"session_id": session_id})
        return session is not None
    

    async def get_user_sessions(self, user_id: str, limit: int = 100):
        pipeline = [
          {"$match": {"user_id": ObjectId(user_id)}},
          {"$sort": {"created_at": -1}},
          {"$limit": limit},
          {"$lookup": {
              "from": self.chat_histories_collection.name,
              "localField": "history_id",
              "foreignField": "_id",
              "as": "sessions"
          }}
        ]
        sessions = await self.chat_unique_sessions_collection.aggregate(pipeline).to_list(length=limit)
        return [await self.serialize_session(s) for s in sessions]


    async def save_user_query(self, user_id: str, query: str, response: str, session_id: str):
        session = await self.chat_unique_sessions_collection.find_one({"session_id": ObjectId(session_id)})

        result = await self.chat_histories_collection.update_one({"_id": session["history_id"] if session else ObjectId()}, {
            "$push": {
                "histories": {
                    "query": query,
                    "response": response,
                    "timestamp": datetime.now(timezone.utc)
                }
            }
        }, upsert=True)
        logger.debug(f"Chat history saved for user: {user_id}, session: {session_id}, result: {result.upserted_id if result.upserted_id else 'updated'}")    
        if session is None:
            await self.chat_unique_sessions_collection.update_one(
                {"session_id": session_id if session_id else str(ObjectId())},
                {"$setOnInsert": {
                    "session_id": ObjectId(session_id),
                    "user_id": ObjectId(user_id),
                    "history_id": ObjectId(result.upserted_id),
                    "created_at": datetime.now(timezone.utc)
                }}, upsert=True
            )

    async def get_single_history(self, user_id: str, history_id: str):
        history = await self.chat_histories_collection.find_one({"_id": ObjectId(history_id), "user_id": ObjectId(user_id)})
        return await self.serialize(history) if history else None

    async def delete_history(self, history_id: str):
        result = await self.chat_histories_collection.delete_one({"_id": ObjectId(history_id)})
        return result.deleted_count > 0


    async def serialize_session(self, session: dict):
        return {
            "id": str(session["_id"]),
            "history_id": str(session["history_id"]),
            "session_id": str(session["session_id"]),
            "user_id": str(session["user_id"]),
            "created_at": str(session["created_at"].isoformat()),
            "sessions": [await self.serialize(history) for history in session["sessions"]] if "sessions" in session else []
        }
    
    async def serialize_history_item(self, item: dict):
        return {
            "query": item["query"],
            "response": item["response"],
            "timestamp": str(item["timestamp"].isoformat()) if "timestamp" in item else None
        }
    
    async def serialize(self, history: dict):
        return {
            "id": str(history["_id"]),
            "histories": [await self.serialize_history_item(item) for item in history["histories"] ] if "histories" in history else []
        }