import logging
import os
from dotenv import load_dotenv
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient
load_dotenv()



logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "myapp")



ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Test@123!")




client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)

db = client[MONGO_DB_NAME]
user_collection = db.users
role_collection = db.roles
tenant_collection = db.tenants
settings_collection = db.settings

async def ensure_indexes():
    try:
        await client.admin.command('ping')  # Test the connection
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        return

    await user_collection.create_index("email", unique=True)
    await role_collection.create_index("name", unique=True)
    await tenant_collection.create_index("name", unique=True)
    await settings_collection.create_index("provider", unique=True)


async def get_db_reference(request: Request):
    db_reference = db
    if hasattr(request.state, "db") and request.state.db != None:
        db_reference = request.state.db
    return db_reference
