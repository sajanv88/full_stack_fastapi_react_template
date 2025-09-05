from datetime import datetime
import os
from typing import Any, List
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import AsyncMongoClient

from app.models.user import Gender
from app.core.password import get_password_hash
from app.models.role import RoleType
from app.core.permission import Permission
from app.models.user import User
from app.models.role import Role

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "myapp")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Test@123!")




client = AsyncMongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
user_collection = db.users
role_collection = db.roles

async def ensure_indexes():
    await user_collection.create_index("email", unique=True)
    await role_collection.create_index("name", unique=True)


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

    print("User fields Current:", user_fields)
    print("Role fields Current:", role_fields)

    if all(field.get_name() in user_fields and field.get_name() in role_fields for field in new_fields):
        print("No new fields to add.")
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

    print("User fields Now:", user_fields)
    print("Role fields Now:", role_fields)


async def seed_default_data():
    print("Seeding default data...")
    # create default admin user
    existing_user = await user_collection.find_one({"email": ADMIN_EMAIL})
    if not existing_user:
        print(f"Creating default admin user: {ADMIN_EMAIL}")
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
        print(f"Admin user already exists: {ADMIN_EMAIL}. Hence, skipping...")

    roles = [
        {"name": RoleType.ADMIN, "description": "Admin role can give full access to application. Can read, write and delete any resource.", "permissions": [Permission.FULL_ACCESS]},
        {"name": RoleType.USER, "description": "Regular user has read and update their own resources.", "permissions": [Permission.USER_SELF_READ_AND_WRITE_ONLY, Permission.USER_VIEW_ONLY, Permission.ROLE_VIEW_ONLY]},
        {"name": RoleType.GUEST, "description": "Guest user has read only access to resources.", "permissions": [Permission.USER_VIEW_ONLY, Permission.ROLE_VIEW_ONLY]}
    ]

    print("Seeding roles...")
    if await role_collection.count_documents({}) != len(roles):
        print("Roles collection is empty or outdated. Seeding roles...")
        for role in roles:
            role["created_at"] = datetime.utcnow()
            await role_collection.find_one_and_replace({"name": role["name"]}, role, upsert=True)
            print(f"Role upserted: {role['name']}")

    admin_role = await role_collection.find_one({"name": RoleType.ADMIN})
    admin_user = await user_collection.find_one({"email": ADMIN_EMAIL})
    if admin_role and admin_user :
        if "role_id" in admin_user and admin_user["role_id"] == admin_role["_id"]:
            print(f"Admin user already has admin role assigned. Hence, skipping...")
        else:
            print(f"Assigning admin role to user: {ADMIN_EMAIL}")
            await user_collection.update_one(
                {"email": ADMIN_EMAIL},
                {"$set": {"role_id": ObjectId(admin_role["_id"])}}
            )

    print("Seeding completed.")
    # Example:
    # await check_new_fields_and_add([DBField("users", "created_at", datetime.utcnow()), DBField("roles", "created_at", datetime.utcnow())])