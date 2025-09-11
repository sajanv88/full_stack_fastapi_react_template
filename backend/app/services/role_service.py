from app.models.role import Role
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
import logging

logger = logging.getLogger(__name__)

class RoleService():
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.role_collection: AsyncIOMotorCollection = db.roles

    async def total_count(self):
        return await self.role_collection.count_documents({})

    async def find_by_name(self, name: str):
        role = await self.role_collection.find_one({"name": name})
        if role is None:
            raise Exception(f"Role not found: {name}")
        return await self.serialize(role)
    
    async def get_role(self, role_id: str):
        role = await self.role_collection.find_one({"_id": ObjectId(role_id)})
        if role is None:
            raise Exception(f"Role not found: {role_id}")
        return await self.serialize(role)
        
    async def create_role(self, role_data: dict):
        try:
            result = await self.role_collection.insert_one(role_data)
            logger.info(f"Role created: {result.inserted_id}")
            return result
        except Exception as error:
            raise error

    async def update_role(self, role_id: str, role_data: dict):
        try:
            result = await self.role_collection.update_one({"_id": ObjectId(role_id)}, {"$set": role_data})
            logger.info(f"Role updated: {role_id}")
            return result
        except Exception as error:
            raise error

    async def delete_role(self, role_id: str):
        try:
            result = await self.role_collection.delete_one({"_id": ObjectId(role_id)})
            logger.info(f"Role deleted: {role_id}")
            return result
        except Exception as error:
            raise error

    async def list_roles(self, skip: int = 0, limit: int = 10):
        try:
            roles = await self.role_collection.find().skip(skip).limit(limit).to_list(length=limit)
            return [await self.serialize(role) for role in roles]
        except Exception as error:
            raise error

    async def serialize(self, role: Role):
        return {
            "id": str(role["_id"]),
            "name": role["name"],
            "description": role["description"],
            "permissions": role["permissions"],
            "created_at": str(role["created_at"]) if "created_at" in role else None
        }


