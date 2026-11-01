import asyncio
from contextvars import Token
from typing import Sequence
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from beanie import Document, UnionDoc, View, init_beanie
from api.common.tenant_context import set_active_database
from api.common.utils import get_logger
from api.core.config import settings
from api.domain.entities.ai import ChatHistoryAI, ChatSessionAI
from api.domain.entities.branding import Branding
from api.domain.entities.notification_settings import NotificationBannerSetting
from api.domain.entities.role import Role
from api.domain.entities.sso_settings import SSOSettings
from api.domain.entities.storage_settings import StorageSettings
from api.domain.entities.stripe_settings import BillingRecord, StripeSettings
from api.domain.entities.subscription_plan import SubscriptionPlan
from api.domain.entities.tenant import Tenant
from api.domain.entities.user import User
from api.domain.entities.user_magic_link import UserMagicLink
from api.domain.entities.user_passkey import UserPasskey, Challenges
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
    ChatSessionAI,
    UserPasskey,
    Challenges,
    UserMagicLink,
    StripeSettings,
    BillingRecord,
    SubscriptionPlan,
    NotificationBannerSetting,
    SSOSettings,
    Branding
]
class Database:
    def __init__(self, uri: str, models: Sequence[type[Document] | type[UnionDoc] | type[View] | str] | None = None) -> None:
        self.client = AsyncMongoClient(uri)
        self.models = models
        logger.debug("Database initializing...")
        self._prepared_tenant_databases: set[str] = set()
        self._prepare_lock = asyncio.Lock()

    def _tenant_models(self) -> list:
        return [model for model in self.models if model != Tenant]

    async def init_db(self, db_name: str, is_tenant: bool | None) -> None:
        """Bind Beanie to a database for the whole process. For startup and background tasks, use `use_database` for requests."""
        self.db: AsyncDatabase = self.client[db_name]
        set_active_database(self.db)
        if self.models:
            if is_tenant:
                await init_beanie(self.db, document_models=self._tenant_models())
                self._prepared_tenant_databases.add(db_name)
                logger.debug("Database models are initialized for new tenant.")
            else:
                await self.init_models()
                logger.debug("Database models are initialized.")

    async def init_models(self) -> None:
        await init_beanie(self.db, document_models=self.models)

    async def use_database(self, db_name: str, is_tenant: bool) -> Token:
        """
        Route the current request to a database without touching process-wide state, so concurrent
        requests of other tenants are unaffected. Pass the returned token to `reset_active_database`.
        """
        database: AsyncDatabase = self.client[db_name]
        token = set_active_database(database)
        if is_tenant and self.models and db_name not in self._prepared_tenant_databases:
            async with self._prepare_lock:
                if db_name not in self._prepared_tenant_databases:
                    await init_beanie(database, document_models=self._tenant_models())
                    self._prepared_tenant_databases.add(db_name)
                    logger.debug(f"Prepared database: {db_name}")
        return token

    async def get_database(self) -> AsyncDatabase:
        return self.db

    async def close(self) -> None:
        await self.client.close()
        logger.warning("Database connection has been closed.")
    
    async def drop(self) -> None:
        await self.client.drop_database(self.db)
        logger.warning("Database has been deleted")

mongo_client = Database(
    uri=settings.mongo_uri,
    models=models
)