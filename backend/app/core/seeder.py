import logging
from datetime import datetime
from typing import Any, List
from bson import ObjectId
from app.models.user import Gender
from app.core.password import get_password_hash
from app.models.role import RoleType
from app.core.permission import Permission
from app.core.db import user_collection, role_collection
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

import os
from app.core.utils import is_tenancy_enabled

from faker import Faker

logger = logging.getLogger(__name__)
fake = Faker()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Test@123!")




async def generate_fake_users(range_count: int = 100, restart: bool = False):
    total_users = await user_collection.count_documents({})
    if total_users >= range_count:
        logger.info(f"Users collection already has {total_users} users. Skipping fake user generation.")
        return
    
    if restart:
        await user_collection.delete_many({
            "email": {"$ne": ADMIN_EMAIL}
        })  # Clear existing users for fresh seeding

    logger.info(f"Generating {range_count} fake users...")
    guest_role = await role_collection.find_one({"name": RoleType.GUEST})
    for _ in range(range_count):
        fake_user = {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "gender": fake.random_element(elements=[Gender.MALE.value, Gender.FEMALE.value, Gender.PREFER_NOT_TO_SAY.value, Gender.OTHER.value]),
            "password": get_password_hash("Test@123!"),
            "is_active": fake.boolean(),
            "role_id": ObjectId(guest_role["_id"]),
            "created_at": datetime.utcnow(),
            "image_url": fake.image_url()
        }
        await user_collection.insert_one(fake_user)
    logger.info("Fake users generated successfully.")


class DBField:
    def __init__(self, collection_name: str, field: str, default_value: Any = None):
        self.collection_name = collection_name
        self.field = field
        self.default_value = default_value

    def get_name(self):
        return self.collection_name

    def get_field(self):
        return self.field

    def get_default_value(self):
        return self.default_value



# Extend this method or add any new fields in the exsiting models.
#  If you created a new model you can add it here for new field extensions
async def check_new_fields_and_add(new_fields: List[DBField] = []):
    # Check for new fields in user and role collections
    user_fields = set()
    role_fields = set()

    async for user in user_collection.find():
        user_fields.update(user.keys())
    async for role in role_collection.find():
        role_fields.update(role.keys())

    logger.info("User fields Current:", user_fields)
    logger.info("Role fields Current:", role_fields)

    if all(field.get_name() in user_fields and field.get_name() in role_fields for field in new_fields):
        logger.info("No new fields to add.")
        return
    
    for field in new_fields:
        if field.get_name() == "users":
            await user_collection.update_many({}, {"$set": {field.get_field(): field.get_default_value()}})
        elif field.get_name() == "roles":
            await role_collection.update_many({}, {"$set": {field.get_field(): field.get_default_value()}})



    async for user in user_collection.find():
        user_fields.update(user.keys())
    async for role in role_collection.find():
        role_fields.update(role.keys())

    logger.info("User fields Now:", user_fields)
    logger.info("Role fields Now:", role_fields)


async def seed_default_data():
    logger.info("Seeding default data...")
    # create default admin user
    existing_user = await user_collection.find_one({"email": ADMIN_EMAIL})
    if not existing_user:
        logger.info(f"Creating default admin user: {ADMIN_EMAIL}")
        hashed_password = get_password_hash(ADMIN_PASSWORD)
        admin_user = {
            "first_name": "Admin",
            "last_name": "Admin",
            "gender": Gender.PREFER_NOT_TO_SAY.value,
            "email": ADMIN_EMAIL,
            "password": hashed_password,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        await user_collection.insert_one(admin_user)
    else:
        logger.info(f"Admin user already exists: {ADMIN_EMAIL}. Hence, skipping...")

    roles = [
        {"name": RoleType.ADMIN, "description": "Admin role can give full access to application. Can read, write and delete any resource.", "permissions": [Permission.FULL_ACCESS]},
        {"name": RoleType.USER, "description": "Regular user has read and update their own resources.", "permissions": [Permission.USER_SELF_READ_AND_WRITE_ONLY, Permission.USER_VIEW_ONLY, Permission.ROLE_VIEW_ONLY]},
        {"name": RoleType.GUEST, "description": "Guest user has read only access to resources.", "permissions": [Permission.USER_VIEW_ONLY, Permission.ROLE_VIEW_ONLY]}
    ]

    if is_tenancy_enabled():
        roles.append({"name": RoleType.HOST, "description": "Host role can manage tenants.", "permissions": [Permission.HOST_MANAGE_TENANTS, Permission.FULL_ACCESS]})

    logger.info("Seeding roles...")
    if await role_collection.count_documents({}) != len(roles):
        logger.info("Roles collection is empty or outdated. Seeding roles...")
        for role in roles:
            role["created_at"] = datetime.utcnow()
            await role_collection.find_one_and_replace({"name": role["name"]}, role, upsert=True)
            logger.info(f"Role upserted: {role['name']}")

    admin_user = await user_collection.find_one({"email": ADMIN_EMAIL})

    if is_tenancy_enabled():
        host_role = await role_collection.find_one({"name": RoleType.HOST})
        if host_role and admin_user:
            if "role_id" in admin_user and admin_user["role_id"] == host_role["_id"]:
                logger.info(f"Admin user already has host role assigned. Hence, skipping...")
            else:
                logger.info(f"Assigning host role to user: {ADMIN_EMAIL}")
                await user_collection.update_one(
                    {"email": ADMIN_EMAIL},
                    {"$set": {"role_id": ObjectId(host_role["_id"])}}
                )
    else:
        logger.info("Seeding admin role...")
        admin_role = await role_collection.find_one({"name": RoleType.ADMIN})
        if admin_role and admin_user :
            if "role_id" in admin_user and admin_user["role_id"] == admin_role["_id"]:
                logger.info(f"Admin user already has admin role assigned. Hence, skipping...")
            else:
                print(f"Assigning admin role to user: {ADMIN_EMAIL}")
                await user_collection.update_one(
                    {"email": ADMIN_EMAIL},
                    {"$set": {"role_id": ObjectId(admin_role["_id"])}}
                )

    # Uncomment to generate fake users when you need feed fake users
    # await generate_fake_users(200) 
    logger.info("Seeding completed.")
    # Example:
    # await check_new_fields_and_add([DBField("users", "created_at", datetime.utcnow()), DBField("roles", "created_at", datetime.utcnow())])



# Invoke this only when a new tenant is created.
class SeedDataForNewlyCreatedTenant:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.user_collection: AsyncIOMotorCollection = db.users
        self.role_collection: AsyncIOMotorCollection = db.roles
    
    async def fill_roles(self, admin_email: str):
        logger.info(f"Filling roles for admin user: {admin_email}")
        roles = [
            {"name": RoleType.ADMIN, "description": "Admin role can give full access to application. Can read, write and delete any resource.", "permissions": [Permission.FULL_ACCESS]},
            {"name": RoleType.USER, "description": "Regular user has read and update their own resources.", "permissions": [Permission.USER_SELF_READ_AND_WRITE_ONLY, Permission.USER_VIEW_ONLY, Permission.ROLE_VIEW_ONLY]},
            {"name": RoleType.GUEST, "description": "Guest user has read only access to resources.", "permissions": [Permission.USER_VIEW_ONLY, Permission.ROLE_VIEW_ONLY]}
        ]
        if await self.role_collection.count_documents({}) != len(roles):
            print("Roles collection is empty or outdated. Seeding roles...")
            for role in roles:
                role["created_at"] = datetime.utcnow()
                await self.role_collection.find_one_and_replace({"name": role["name"]}, role, upsert=True)
                logger.info(f"Role upserted: {role['name']}")

        admin_role = await self.role_collection.find_one({"name": RoleType.ADMIN})
        await self.user_collection.update_one(
            {"email": admin_email},
            {"$set": {"role_id": ObjectId(admin_role["_id"])}}
        )

