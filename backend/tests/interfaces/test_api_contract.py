from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from tests.factories import seed_user


async def test_unknown_api_route_is_a_json_404_not_the_spa(client: AsyncClient):
    response = await client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"
    assert response.json()["error"] == "API endpoint not found."


async def test_spa_routes_are_still_served(client: AsyncClient):
    response = await client.get("http://test/dashboard")

    assert response.status_code == 200


async def test_validation_errors_carry_the_error_contract(client: AsyncClient):
    """`detail` stays FastAPI's list, `error` is what extractErrorMessage reads in the frontend."""
    response = await client.post("/users/", json={"email": "not-an-email"})

    assert response.status_code == 422
    body = response.json()
    assert isinstance(body["detail"], list)
    assert isinstance(body["error"], str)
    assert body["code"] == 422


async def test_api_errors_keep_their_shape(client: AsyncClient):
    response = await client.get("/roles/68c3031f449ed3590028c778")

    assert response.json() == {
        "error": "Role with identifier 68c3031f449ed3590028c778 not found.",
        "code": 404,
        "detail": "Role with identifier 68c3031f449ed3590028c778 not found.",
    }


async def test_malformed_ids_are_not_found_instead_of_a_500(client: AsyncClient):
    assert (await client.get("/users/not-an-id")).status_code == 404
    assert (await client.get("/roles/not-an-id")).status_code == 404


async def test_malformed_ids_elsewhere_are_a_client_error(client: AsyncClient):
    response = await client.get("/ai/sessions/not-an-id")

    assert response.status_code == 400
    assert response.json()["error"] == "The given identifier is not valid."


async def test_unexpected_failures_return_the_error_contract(test_app):
    transport = ASGITransport(app=test_app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test/api/v1") as client:
        with patch("api.usecases.role_service.RoleService.list_roles", AsyncMock(side_effect=RuntimeError("secret detail"))):
            response = await client.get("/roles/")

    assert response.status_code == 500
    assert response.json()["error"] == "Internal server error."
    assert "secret detail" not in response.text


@pytest.mark.parametrize("path", ["/users/", "/roles/", "/tenants/", "/audit-logs/"])
@pytest.mark.parametrize("query", ["skip=-1", "limit=0", "limit=-1", "limit=1001"])
async def test_pagination_bounds(client: AsyncClient, path, query):
    response = await client.get(f"{path}?{query}")

    assert response.status_code == 422


async def test_every_response_has_security_headers(client: AsyncClient):
    for path in ["/health/", "/does-not-exist"]:
        headers = (await client.get(path)).headers

        assert headers["x-content-type-options"] == "nosniff"
        assert headers["x-frame-options"] == "SAMEORIGIN"
        assert headers["referrer-policy"] == "strict-origin-when-cross-origin"


async def test_health_stays_a_shallow_check(client: AsyncClient):
    response = await client.get("/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "Ok"}


async def test_readiness_reports_dependencies(client: AsyncClient):
    response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "Ok", "checks": {"mongodb": True, "redis": True}}


async def test_readiness_fails_when_a_dependency_is_down(client: AsyncClient):
    with patch("api.interfaces.api_controllers.health_endpoint.redis_client") as redis:
        redis.ping = AsyncMock(side_effect=ConnectionError("down"))
        response = await client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["checks"] == {"mongodb": True, "redis": False}


async def test_users_never_expose_password_hashes(client: AsyncClient):
    user = await seed_user()

    single = await client.get(f"/users/{user.id}")
    listed = await client.get("/users/")

    assert "password" not in single.json()
    assert "password" not in listed.json()["users"][0]
