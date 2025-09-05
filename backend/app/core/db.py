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


