import os
from dotenv import load_dotenv
from pymongo import AsyncMongoClient

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "myapp")
client = AsyncMongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
user_collection = db.users

async def ensure_indexes():
    await user_collection.create_index("email", unique=True)


