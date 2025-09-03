import os
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import AsyncMongoClient

from app.models.user import Gender
from app.core.password import get_password_hash
from app.models.role import RoleType
from app.core.permission import Permission

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
            "is_active": True
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
            await role_collection.find_one_and_replace({"name": role["name"]}, role, upsert=True)
            print(f"Role upserted: {role['name']}")

    admin_role = await role_collection.find_one({"name": RoleType.ADMIN})
    if admin_role:
        print(f"Assigning admin role to user: {ADMIN_EMAIL}")
        await user_collection.update_one(
            {"email": ADMIN_EMAIL},
            {"$set": {"role_id": ObjectId(admin_role["_id"])}}
        )

    print("Seeding completed.")