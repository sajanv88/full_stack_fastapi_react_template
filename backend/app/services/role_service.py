from app.models.role import Role
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection


class RoleService():
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.role_collection: AsyncIOMotorCollection = db.roles

    async def total_count(self):
        return await self.role_collection.count_documents({})

    async def find_by_name(self, name: str):
        try:
            role = await self.role_collection.find_one({"name": name})
            return await self.serialize(role)
        except Exception as error:
            print("Error finding role by name:", error)
            return None

    async def get_role(self, role_id: str):
        try:
            role = await self.role_collection.find_one({"_id": ObjectId(role_id)})
            return await self.serialize(role)
        except Exception as error:
            print("Error getting role:", error)
            return None

    async def create_role(self, role_data: dict):
        return await self.role_collection.insert_one(role_data)

    async def update_role(self, role_id: str, role_data: dict):
       return await self.role_collection.update_one({"_id": ObjectId(role_id)}, {"$set": role_data})

    async def delete_role(self, role_id: str):
        return await self.role_collection.delete_one({"_id": ObjectId(role_id)})

    async def list_roles(self, skip: int = 0, limit: int = 10):
        roles = await self.role_collection.find().skip(skip).limit(limit).to_list(length=limit)
        return [await self.serialize(role) for role in roles]

    async def serialize(self, role: Role):
        return {
            "id": str(role["_id"]),
            "name": role["name"],
            "description": role["description"],
            "permissions": role["permissions"],
            "created_at": str(role["created_at"]) if "created_at" in role else None
        }


