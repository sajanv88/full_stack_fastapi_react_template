from app.models.user import User
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
import logging

logger = logging.getLogger(__name__)

class UserService():
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.user_collection: AsyncIOMotorCollection = db.users

    async def total_count(self, params: dict = {}):
        return await self.user_collection.count_documents(params)

    async def find_by_email(self, email:str):
   
        user = await self.user_collection.find_one({"email": email})
        if user is None:
            raise Exception(f"User not found: {email}")
        return await self.serialize(user)
  

    async def get_raw_find_by_email(self, email: str):
        try:
            user = await self.user_collection.find_one({"email": email})
            return user
        except Exception as error:
            raise error

    async def get_user(self, user_id: str):
        user = await self.user_collection.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise Exception(f"User not found: {user_id}")
        return await self.serialize(user)
   

    async def create_user(self, user_data: dict):
        try:
            return await self.user_collection.insert_one(user_data)
        except Exception as error:
            raise error

    async def update_user(self, user_id: str, user_data: dict):
        try:
            return await self.user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": user_data})
        except Exception as error:
            raise error

    async def delete_user(self, user_id: str):
        try:
            return await self.user_collection.delete_one({"_id": ObjectId(user_id)})
        except Exception as error:
            raise error

    async def list_users(self, skip: int = 0, limit: int = 10):
        try:
            users = await self.user_collection.find().skip(skip).limit(limit).to_list(length=limit)
            return [await self.serialize(user) for user in users]
        except Exception as error:
            raise error

    async def assign_role(self, user_id:str,  role_id: str):
        try:
            return await self.user_collection.update_one({"_id": ObjectId(user_id)}, {
                "$set": {
                    "role_id": ObjectId(role_id)
                }
            })
        except Exception as error:
            raise error

    async def remove_role(self, user_id:str):
        try:
            return await self.user_collection.update_one({"_id": ObjectId(user_id)}, {
                "$set": {
                    "role_id": None
                }
            })
        except Exception as error:
            raise error


    async def serialize(self, user: User):
        return {
            "id": str(user["_id"]),
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "gender": user["gender"],
            "role_id": str(user["role_id"]) if "role_id" in user and user["role_id"] else None,
            "is_active": user["is_active"],
            "activated_at": str(user["activated_at"]) if "activated_at" in user else None,
            "created_at": str(user["created_at"]) if "created_at" in user else None,
            "image_url": user["image_url"] if "image_url" in user else None,
            "tenant_id": str(user["tenant_id"]) if "tenant_id" in user and user["tenant_id"] else None
        }

