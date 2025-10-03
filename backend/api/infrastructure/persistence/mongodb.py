from typing import Sequence
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from beanie import Document, UnionDoc, View, init_beanie
from api.common.utils import get_logger
from api.core.config import settings
from api.domain.entities.ai import ChatHistoryAI, ChatSessionAI
from api.domain.entities.role import Role
from api.domain.entities.storage_settings import StorageSettings
from api.domain.entities.tenant import Tenant
from api.domain.entities.user import User
from api.domain.entities.user_password_reset import UserPasswordReset
from api.domain.entities.user_preference import UserPreference
logger = get_logger(__name__)

models = [
    User,
    Tenant,
    Role,
    UserPasswordReset,
    UserPreference,
    StorageSettings,
    ChatHistoryAI,
    ChatSessionAI
]
class Database:
    def __init__(self, uri: str, models: Sequence[type[Document] | type[UnionDoc] | type[View] | str] | None = None) -> None:
        self.client = AsyncMongoClient(uri)
        self.models = models
        logger.debug("Database initializing...")
        self.is_tenant = False
        
    
    async def init_db(self, db_name: str, is_tenant: bool | None) -> None:
        self.db: AsyncDatabase = self.client[db_name]
        if self.models:
            if is_tenant:
                self.is_tenant = True
                tenant_models = [model for model in self.models if model != Tenant]
                await init_beanie(self.db, document_models=tenant_models)
                logger.debug("Database models are initialized for new tenant.")
            else:
                await self.init_models()
                logger.debug("Database models are initialized.")

    async def init_models(self) -> None:
        await init_beanie(self.db, document_models=self.models)

    async def get_database(self) -> AsyncDatabase:
        return self.db

    async def close(self) -> None:
        await self.client.close()
        logger.warning("Database connection has been closed.")
    
    async def drop(self) -> None:
        await self.client.drop_database(self.db)
        logger.warning("Database has been deleted")

    def is_tenant_active(self) -> bool:
        return self.is_tenant

mongo_client = Database(
    uri=settings.mongo_uri,
    models=models
)