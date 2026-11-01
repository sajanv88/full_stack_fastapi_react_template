import json
from typing import Any

from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import Request
from api.common.security import extract_bearer_token
from api.common.utils import get_logger
from api.core.container import get_jwt_token_service
from api.infrastructure.externals.redis_client import redis_client as redis

logger = get_logger(__name__)

redis_cache_expiry = 300  # Cache expiry time in seconds (5 minutes)

not_allowed_cache_paths = [
    "/api/v1/account/login",
    "/api/v1/account/logout",
    "/api/v1/account/register",
    "/api/v1/account/refresh",
    "/api/v1/account/me",
    "/api/v1/app_configuration/",
    "/api/v1/security/passkeys",
    "/api/v1/configurations/stripe/webhooks",
    "/api/v1/health/",
    "/api/v1/health/ready",
]


class RedisCacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, expiry: int = redis_cache_expiry):
        super().__init__(app)
        self.expiry = expiry

    async def _clear_cache(self, user_id: str, tenant_id: str) -> None:
        try:
            async for key in redis.scan_iter(f"cache:cu{user_id}:ct{tenant_id}:*"):
                await redis.delete(key)
        except (RedisError, OSError) as e:
            logger.warning(f"Could not clear cache: {e}")

    async def _read_cache(self, cache_key: str) -> dict[str, Any] | None:
        try:
            cached_value = await redis.get(cache_key)
        except (RedisError, OSError) as e:
            logger.warning(f"Could not read cache: {e}")
            return None
        return json.loads(cached_value) if cached_value else None

    async def _write_cache(self, cache_key: str, body: bytes, content_type: str) -> None:
        try:
            to_cache = json.dumps({
                "body": body.decode(),
                "status": 200,
                "media_type": content_type,
            })
            await redis.set(cache_key, to_cache, ex=self.expiry)
        except (RedisError, OSError, UnicodeDecodeError) as e:
            logger.warning(f"Could not write cache: {e}")

    async def dispatch(self, request: Request, call_next):
        token = extract_bearer_token(request.headers.get("authorization"))
        path = request.url.path

        if token is None or not path.startswith("/api/") or any(path.endswith(p) for p in not_allowed_cache_paths):
            logger.debug(f"Bypassing cache for path: {path}")
            return await call_next(request)

        # Requests that can't be tied to a user must never share a cache entry.
        payload = await get_jwt_token_service().decode_token(token, type="access_token")
        if payload is None:
            return await call_next(request)

        user_id = str(payload.sub)
        tenant_id = str(getattr(request.state, "tenant_id", None) or "default")

        # Clear after the write has happened, otherwise a concurrent read can re-cache stale data.
        if request.method != "GET":
            response = await call_next(request)
            await self._clear_cache(user_id, tenant_id)
            return response

        cache_key = f"cache:cu{user_id}:ct{tenant_id}:{path}?{request.url.query}"
        cached = await self._read_cache(cache_key)
        if cached:
            logger.debug(f"Cache hit for key: {cache_key}")
            return Response(
                content=cached["body"],
                status_code=cached["status"],
                media_type=cached["media_type"],
            )

        response = await call_next(request)

        if response.status_code == 401:
            await self._clear_cache(user_id, tenant_id)
            return response

        # Anything else is passed through untouched, so binary and streaming bodies keep working.
        content_type = response.headers.get("content-type", "")
        if response.status_code != 200 or "application/json" not in content_type:
            return response

        body = b"".join([chunk async for chunk in response.body_iterator])
        await self._write_cache(cache_key, body, content_type)

        # Return new Response (since body_iterator is consumed)
        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=content_type,
        )
