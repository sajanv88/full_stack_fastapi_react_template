import json
from redis.asyncio import Redis, from_url
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import Request
from api.common.utils import get_logger
from api.core.config import settings

from api.core.container import get_jwt_token_service, get_role_service, get_user_service
from api.infrastructure.security.current_user import  current_user_optional

logger = get_logger(__name__)

redis_cache_expiry = 300  # Cache expiry time in seconds (5 minutes)
redis: Redis =  from_url(url=settings.redis_uri, decode_responses=True)

class RedisCacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, expiry: int = redis_cache_expiry):
        super().__init__(app)
        self.expiry = expiry

    async def dispatch(self, request: Request, call_next):
       
        try:
            token = None
            if "authorization" in request.headers:
                token = request.headers["authorization"].replace("Bearer ", "")

            user_service = get_user_service()
            jwt_service = get_jwt_token_service()
            role_service = get_role_service()

            current_user = await current_user_optional(
                token,
                user_service=user_service,
                token_service=jwt_service,
                role_service=role_service,
            )
        except Exception as e:
            logger.debug(f"Could not resolve current_user in middleware: {e}")
            current_user = None

        user_id = getattr(current_user, "id", "anonymous")
        tenant_id = getattr(current_user, "tenant_id", "default")
        cache_base = f"cu{user_id}:ct{tenant_id}:{request.url.path}?{request.url.query}"
        logger.debug(f"Cache base string: {cache_base}")
        cache_key = f"cache:{cache_base}"

        logger.debug(request.method + " " + request.url.path + "?" + request.url.query)
        # Only cache GET requests
        if request.method != "GET":
            logger.debug(f"Clearing cache for key: {cache_key}")
            async for key in redis.scan_iter(f"cache:cu{user_id}:ct{tenant_id}:*"):
                await redis.delete(key)
            logger.debug("Cache cleared for non-GET request.")
            return await call_next(request)
           

        # --- Try reading from cache
        cached_value = await redis.get(cache_key)
        if cached_value:
            logger.debug(f"Cache hit for key: {cache_key}")
            cached = json.loads(cached_value)
            return Response(
                content=cached["body"],
                status_code=cached["status"],
                media_type=cached["media_type"],
                headers=cached.get("headers", {}),
            )

        # --- Cache miss → execute route handler
        response = await call_next(request)

        # Read and rebuild response body
        body = b"".join([chunk async for chunk in response.body_iterator])
        body_text = body.decode()
        content_type = response.headers.get("content-type", "")

        # Cache only 200 OK + JSON responses
        if response.status_code == 200  and "application/json" in content_type:
            to_cache = json.dumps({
                "body": body_text,
                "status": response.status_code,
                "media_type": content_type,
            })
            await redis.set(cache_key, to_cache, ex=self.expiry)
            logger.debug(f"Cache set for key: {cache_key}")

        # Return new Response (since body_iterator is consumed)
        return Response(
            content=body_text,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=content_type,
        )