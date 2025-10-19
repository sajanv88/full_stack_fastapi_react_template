import json
from redis.asyncio import Redis, from_url
from api.common.utils import get_logger
from api.core.config import settings


logger = get_logger(__name__)

redis_cache_expiry = 300  # Cache expiry time in seconds (5 minutes)

class CacheBaseRepository:
    def __init__(self, name: str):
        self.redis: Redis =  from_url(url=settings.redis_uri, decode_responses=True)
        self.model_name = name

    def cache_key(self, method: str, *args, **kwargs) -> str:
        """
        Generates a unique cache key for each method and parameters.
        Example: user:list or user:get:123
        """
        base = self.model_name
        # Convert all kwargs values to strings safely
        stringified_kwargs = {k: str(v) for k, v in kwargs.items()}
        key_body = json.dumps(stringified_kwargs, sort_keys=True)
        key = f"{base}:{method}:{key_body}"
        logger.debug(f"Generated cache key: {key}")
        return key


    async def clear_cache(self):
        """
        Clears all cache for this model.
        """
        pattern = f"{self.model_name}:*"
        async for key in self.redis.scan_iter(pattern):
            await self.redis.delete(key)
        logger.debug(f"Cache cleared for {self.model_name}")
    

    async def set_cache(self, key: str, value: str, expiry: int = redis_cache_expiry):
        await self.redis.set(key, value, ex=expiry)
        logger.debug(f"Set cache for key: {key} with expiry: {expiry} seconds")