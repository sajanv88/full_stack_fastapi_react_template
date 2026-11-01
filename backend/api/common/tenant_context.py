from contextvars import ContextVar, Token
from typing import Optional

from pymongo.asynchronous.database import AsyncDatabase

# The database of the current request or task. Beanie keeps its collection binding in
# process-wide class state, so tenant routing has to live here: a ContextVar is isolated
# per asyncio task, which keeps concurrent requests of different tenants apart.
_active_database: ContextVar[Optional[AsyncDatabase]] = ContextVar("active_database", default=None)


def get_active_database() -> Optional[AsyncDatabase]:
    return _active_database.get()


def set_active_database(database: AsyncDatabase) -> Token:
    return _active_database.set(database)


def reset_active_database(token: Token) -> None:
    _active_database.reset(token)
