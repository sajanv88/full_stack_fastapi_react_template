from redis.exceptions import RedisError

from api.common.exceptions import TooManyRequestsException
from api.common.utils import get_logger
from api.infrastructure.externals.redis_client import redis_client

logger = get_logger(__name__)


async def enforce_rate_limit(scope: str, identifier: str, limit: int, window_seconds: int) -> None:
    """
    Fixed-window limiter. Raises TooManyRequestsException once `identifier` exceeds `limit`
    calls in the window. Fails open: a Redis outage must not take logins down with it.
    """
    key = f"ratelimit:{scope}:{identifier.lower()}"
    try:
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, window_seconds)
    except (RedisError, OSError) as e:
        logger.warning(f"Rate limiter unavailable, allowing request: {e}")
        return

    if count > limit:
        raise TooManyRequestsException("Too many attempts. Please try again later.")
