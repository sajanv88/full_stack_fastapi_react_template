from redis.asyncio import Redis, from_url

from api.core.config import settings

# With timeouts, a stalled Redis fails fast and the callers can fail open, instead of hanging requests.
redis_client: Redis = from_url(
    url=settings.redis_uri,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)
