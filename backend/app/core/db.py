import os
from dotenv import load_dotenv
from fastapi import Request
from pymongo import AsyncMongoClient


load_dotenv()


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "myapp")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Test@123!")




client = AsyncMongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
user_collection = db.users
role_collection = db.roles
tenant_collection = db.tenants

async def ensure_indexes():
    await user_collection.create_index("email", unique=True)
    await role_collection.create_index("name", unique=True)
    await tenant_collection.create_index("name", unique=True)


async def get_db_reference(request: Request):
    db_reference = db
    if hasattr(request.state, "db") and request.state.db != None:
        db_reference = request.state.db
    return db_reference
