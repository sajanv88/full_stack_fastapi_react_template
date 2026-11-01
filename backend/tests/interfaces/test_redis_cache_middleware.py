from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from beanie import PydanticObjectId
from httpx import ASGITransport, AsyncClient
from redis.exceptions import ConnectionError as RedisConnectionError
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from api.common.dtos.token_dto import TokenPayloadDto
from api.core.container import get_jwt_token_service
from api.domain.entities.notification_settings import NotificationBannerSetting
from api.infrastructure.externals.redis_client import redis_client
from api.infrastructure.persistence.mongodb import mongo_client
from api.common.tenant_context import reset_active_database
from api.interfaces.middlewares.redis_cache_middleware import RedisCacheMiddleware
from tests.factories import seed_tenant


async def bearer(user_id: str | None = None) -> dict[str, str]:
    token = await get_jwt_token_service().get_access_token(TokenPayloadDto(
        sub=user_id or PydanticObjectId(),
        email="user@example.com",
        is_active=True,
    ))
    return {"Authorization": f"Bearer {token.access_token}"}


class Calls:
    def __init__(self):
        self.count = 0


@pytest.fixture
def probe(test_app):
    """A tiny app behind the real middleware, counting how often its handlers actually run."""
    calls = Calls()

    async def json_route(_request):
        calls.count += 1
        return JSONResponse({"calls": calls.count})

    async def binary_route(_request):
        calls.count += 1
        return Response(b"\xff\xfe\x00binary", media_type="application/json")

    async def unauthorized_route(_request):
        calls.count += 1
        return JSONResponse({"error": "nope"}, status_code=401)

    async def write_route(_request):
        calls.count += 1
        return JSONResponse({}, status_code=201)

    app = Starlette(
        routes=[
            Route("/api/v1/data", json_route),
            Route("/api/v1/data", write_route, methods=["POST"]),
            Route("/api/v1/binary", binary_route),
            Route("/api/v1/unauthorized", unauthorized_route),
        ],
        middleware=[Middleware(RedisCacheMiddleware)],
    )
    return app, calls


def client_for(app) -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def test_get_is_cached_per_user(probe):
    app, calls = probe
    headers = await bearer()
    async with client_for(app) as client:
        first = await client.get("/api/v1/data", headers=headers)
        second = await client.get("/api/v1/data", headers=headers)
        other_user = await client.get("/api/v1/data", headers=await bearer())

    assert first.json() == second.json() == {"calls": 1}
    assert other_user.json() == {"calls": 2}


async def test_write_invalidates_the_users_cache(probe):
    app, calls = probe
    headers = await bearer()
    async with client_for(app) as client:
        await client.get("/api/v1/data", headers=headers)
        await client.post("/api/v1/data", headers=headers)
        after_write = await client.get("/api/v1/data", headers=headers)

    assert after_write.json() == {"calls": 3}


async def test_invalid_tokens_never_touch_the_cache(probe):
    """Regression: they all shared one `anonymous` entry."""
    app, calls = probe
    headers = {"Authorization": "Bearer garbage"}
    async with client_for(app) as client:
        await client.get("/api/v1/data", headers=headers)
        await client.get("/api/v1/data", headers=headers)

    assert calls.count == 2
    assert await redis_client.keys("cache:*") == []


async def test_non_utf8_bodies_pass_through(probe):
    """Regression: the body was decoded unconditionally, which crashed on binary content."""
    app, _calls = probe
    async with client_for(app) as client:
        response = await client.get("/api/v1/binary", headers=await bearer())

    assert response.status_code == 200
    assert response.content == b"\xff\xfe\x00binary"


async def test_a_401_runs_the_handler_once(probe):
    """Regression: on a 401 the middleware called the handler a second time."""
    app, calls = probe
    async with client_for(app) as client:
        response = await client.get("/api/v1/unauthorized", headers=await bearer())

    assert response.status_code == 401
    assert calls.count == 1


@pytest.fixture
def redis_outage():
    broken = MagicMock()
    broken.get = AsyncMock(side_effect=RedisConnectionError("down"))
    broken.set = AsyncMock(side_effect=RedisConnectionError("down"))
    with patch("api.interfaces.middlewares.redis_cache_middleware.redis", broken):
        yield


async def test_a_redis_outage_does_not_take_the_api_down(probe, redis_outage):
    app, _calls = probe
    async with client_for(app) as client:
        response = await client.get("/api/v1/data", headers=await bearer())

    assert response.status_code == 200


async def test_public_responses_are_not_shared_between_tenants(client: AsyncClient, tenant_databases):
    """Regression: the cache key ignored the request tenant, so tenants could read each other's banner."""
    tenants = [await seed_tenant("alpha"), await seed_tenant("beta")]
    tenant_databases.extend(str(t.id) for t in tenants)
    for tenant in tenants:
        token = await mongo_client.use_database(f"tenant_{tenant.id}", is_tenant=True)
        await NotificationBannerSetting(is_enabled=True, message=tenant.name).insert()
        reset_active_database(token)

    # The same user, as a host admin moving between tenants would.
    headers = await bearer()
    for tenant in tenants * 2:
        response = await client.get("/notifications/banner", headers={**headers, "X-Tenant-ID": str(tenant.id)})
        assert response.json()["message"] == tenant.name


async def test_current_user_is_never_cached(client: AsyncClient):
    """Role changes have to apply immediately, not five minutes later."""
    await client.get("/account/me", headers=await bearer())

    assert await redis_client.keys("cache:*") == []
