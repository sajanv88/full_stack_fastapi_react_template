from app.models.user import User
from bson import ObjectId

class UserService():
    def __init__(self, db):
        self.db = db
        self.user_collection = db.users

    async def total_count(self):
        return await self.user_collection.count_documents({})

    async def get_user(self, user_id: str):
        user = await self.user_collection.find_one({"_id": ObjectId(user_id)})
        return await self.serialize(user)

    async def create_user(self, user_data: dict):
        return await self.user_collection.insert_one(user_data)

    async def update_user(self, user_id: str, user_data: dict):
       return await self.user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": user_data})

    async def delete_user(self, user_id: str):
        return await self.user_collection.delete_one({"_id": ObjectId(user_id)})

    async def list_users(self, skip: int = 0, limit: int = 10):
        users = await self.user_collection.find().skip(skip).limit(limit).to_list(length=limit)
        return [await self.serialize(user) for user in users]
    
    async def assign_role(self, user_id:str,  role_id: str):
        return await self.user_collection.update_one({"_id": ObjectId(user_id)}, {
            "$set": {
                "role_id": ObjectId(role_id)
            }
        })
    
    async def remove_role(self, user_id:str):
        return await self.user_collection.update_one({"_id": ObjectId(user_id)}, {
            "$set": {
                "role_id": None
            }
        })


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
            "image_url": user["image_url"] if "image_url" in user else None
        }

