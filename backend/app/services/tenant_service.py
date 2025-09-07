from app.models.tenant import Tenant
from bson import ObjectId
from app.core.db import client
from app.services.users_service import UserService

class TenantService:
    def __init__(self, db):
        self.db = db
        self.tenant_collection = db.tenants

    async def total_count(self):
        return await self.tenant_collection.count_documents({})

    async def create_tenant(self, tenant: dict):
        result = await self.tenant_collection.insert_one(tenant)
        if result.inserted_id:
            tenant_id = await self.get_tenant(str(result.inserted_id))
            user_service = UserService(client[f"tenant_{str(result.inserted_id)}"])
            await user_service.create_user({
                "email": f"user@{tenant['subdomain']}.com",
                "name": "Default User",
                "password": "password"
            })
        return result

    async def get_tenant(self, tenant_id: str):
        tenant = await self.tenant_collection.find_one({"_id": ObjectId(tenant_id)})
        return await self.serialize(tenant)

    async def update_tenant(self, tenant_id: str, tenant: dict):
        return await self.tenant_collection.update_one({"_id": ObjectId(tenant_id)}, {"$set": tenant})

    async def delete_tenant(self, tenant_id: str):
        return await self.tenant_collection.delete_one({"_id": ObjectId(tenant_id)})

    async def list_tenants(self, skip: int = 0, limit: int = 10):
        tenants = await self.tenant_collection.find().skip(skip).limit(limit).to_list(length=limit)
        return [await self.serialize(tenant) for tenant in tenants]

    async def serialize(self, tenant: Tenant):
        return {
            "id": str(tenant["_id"]),
            "name": tenant["name"],
            "subdomain": tenant["subdomain"]
        }
