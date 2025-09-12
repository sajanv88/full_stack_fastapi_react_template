from app.models.tenant import Tenant
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from app.core.db import client
import logging

logger = logging.getLogger(__name__)
class TenantService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.tenant_collection: AsyncIOMotorCollection = db.tenants

    async def total_count(self):
        return await self.tenant_collection.count_documents({})

    async def create_tenant(self, tenant: dict):
        existing_tenant = await self.tenant_collection.find_one({"name": tenant["name"]})
        if existing_tenant:
            raise Exception(f"Tenant with this name '{tenant['name']}' already exists")
        return await self.tenant_collection.insert_one(tenant)
         
    async def get_tenant(self, tenant_id: str):
        tenant = await self.tenant_collection.find_one({"_id": ObjectId(tenant_id)})
        if tenant is None:
            raise Exception(f"Tenant not found: {tenant_id}")
        return await self.serialize(tenant)

    async def find_by_name(self, name: str):
        tenant = await self.tenant_collection.find_one({"name": name})
        if tenant is None:
            raise Exception(f"Tenant not found: {name}")
        return await self.serialize(tenant)

    async def update_tenant(self, tenant_id: str, tenant: dict):
        try:
            return await self.tenant_collection.update_one({"_id": ObjectId(tenant_id)}, {"$set": tenant})
        except Exception as error:
            raise error

    async def delete_tenant(self, tenant_id: str):
        try:
            return await self.tenant_collection.delete_one({"_id": ObjectId(tenant_id)})
        except Exception as error:
            raise error

    async def list_tenants(self, skip: int = 0, limit: int = 10):
        try:
            tenants = await self.tenant_collection.find().skip(skip).limit(limit).to_list(length=limit)
            return [await self.serialize(tenant) for tenant in tenants]
        except Exception as error:
            raise error
        
    async def drop_tenant_db(self, tenant_id: str):
        logger.warning("Drop database request received")
        drop_db = f'tenant_{tenant_id}'
        await client.drop_database(drop_db)
        logger.info(f"Database tenant_{tenant_id} has been deleted successfully.")


    async def serialize(self, tenant: Tenant):
        return {
            "id": str(tenant["_id"]),
            "name": tenant["name"],
            "subdomain": tenant["sub_domain"] if "sub_domain" in tenant else None
        }
