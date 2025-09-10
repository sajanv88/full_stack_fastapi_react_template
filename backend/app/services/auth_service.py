
from motor.motor_asyncio import AsyncIOMotorDatabase
class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
