import asyncio
from unittest.mock import patch

import pytest
from beanie import PydanticObjectId
from httpx import AsyncClient

from api.domain.dtos.role_dto import UpdateRoleDto
from api.domain.entities.notification_settings import NotificationBannerSetting
from api.domain.entities.role import Role
from api.domain.enum.permission import Permission
from api.infrastructure.persistence.mongodb import mongo_client
from api.common.tenant_context import reset_active_database
from tests.factories import make_user, seed_tenant


async def seed_banner(tenant_id: str, message: str) -> None:
    token = await mongo_client.use_database(f"tenant_{tenant_id}", is_tenant=True)
    try:
        await NotificationBannerSetting(is_enabled=True, message=message).insert()
    finally:
        reset_active_database(token)


async def test_concurrent_requests_never_see_another_tenants_data(client: AsyncClient, tenant_databases):
    """Regression: re-binding Beanie per request served 40% of responses from the wrong tenant."""
    alpha, beta = await seed_tenant("alpha"), await seed_tenant("beta")
    tenant_ids = [str(alpha.id), str(beta.id)]
    tenant_databases.extend(tenant_ids)
    for tenant_id in tenant_ids:
        await seed_banner(tenant_id, f"secret-of-{tenant_id}")

    async def read_banner(tenant_id: str) -> tuple[str, str]:
        response = await client.get("/notifications/banner", headers={"X-Tenant-ID": tenant_id})
        assert response.status_code == 200
        return tenant_id, response.json()["message"]

    results = await asyncio.gather(*[read_banner(tenant_ids[i % 2]) for i in range(200)])

    assert all(message == f"secret-of-{tenant_id}" for tenant_id, message in results)


async def test_first_requests_of_new_tenants_race_safely(client: AsyncClient, tenant_databases):
    """The first request of a tenant prepares its database, others must not be disturbed by that."""
    tenants = [await seed_tenant(f"tenant{i}") for i in range(4)]
    tenant_databases.extend(str(t.id) for t in tenants)

    responses = await asyncio.gather(*[
        client.get("/notifications/banner", headers={"X-Tenant-ID": str(tenants[i % 4].id)}) for i in range(40)
    ])

    assert {r.status_code for r in responses} == {200}


async def test_requests_without_a_tenant_stay_on_the_host_database(client: AsyncClient, tenant_databases):
    tenant = await seed_tenant()
    tenant_databases.append(str(tenant.id))
    await seed_banner(str(tenant.id), "tenant banner")

    tenant_response = await client.get("/notifications/banner", headers={"X-Tenant-ID": str(tenant.id)})
    host_response = await client.get("/notifications/banner")

    assert tenant_response.json()["message"] == "tenant banner"
    assert host_response.json()["message"] is None


async def test_malformed_tenant_id_is_a_client_error(client: AsyncClient):
    response = await client.get("/notifications/banner", headers={"X-Tenant-ID": "not-an-id"})

    assert response.status_code == 400
    assert response.json()["error"] == "Invalid tenant ID."


async def test_unknown_tenant_gets_no_database(client: AsyncClient):
    """Any caller can send this header, it must not be able to create databases."""
    unknown = str(PydanticObjectId())

    response = await client.get("/notifications/banner", headers={"X-Tenant-ID": unknown})

    assert response.status_code == 404
    assert f"tenant_{unknown}" not in await mongo_client.client.list_database_names()


async def test_spa_pages_ignore_the_tenant_query_parameter(client: AsyncClient):
    """Email links carry ?tenant_id=, the page itself has to load whatever that value is."""
    response = await client.get("http://test/activation?tenant_id=not-an-id")

    assert response.status_code == 200


@pytest.mark.parametrize("method, path", [
    ("get", "/tenants/"),
    ("get", "/features/"),
])
async def test_tenant_admin_can_not_use_host_endpoints(client: AsyncClient, act_as, method, path):
    """Regression: the full access override also satisfied host permissions."""
    act_as(make_user([Permission.FULL_ACCESS], tenant_id=str(PydanticObjectId())))

    response = await getattr(client, method)(path)

    assert response.status_code == 403


async def test_tenant_admin_can_not_delete_another_tenant(client: AsyncClient, act_as):
    victim = await seed_tenant("victim")
    act_as(make_user([Permission.FULL_ACCESS], tenant_id=str(PydanticObjectId())))

    response = await client.delete(f"/tenants/{victim.id}")

    assert response.status_code == 403


async def test_host_permission_on_a_tenant_role_grants_nothing(client: AsyncClient, act_as):
    """Roles that were already escalated stay in the database, they must be inert."""
    act_as(make_user([Permission.HOST_MANAGE_TENANTS], tenant_id=str(PydanticObjectId())))

    response = await client.get("/tenants/")

    assert response.status_code == 403


async def test_tenant_admin_can_not_grant_host_permissions(client: AsyncClient, act_as):
    role = await Role(name="custom", description=None).insert()
    act_as(make_user([Permission.FULL_ACCESS], tenant_id=str(PydanticObjectId())))

    response = await client.put(
        f"/roles/{role.id}",
        json=UpdateRoleDto(name="custom", permissions=[Permission.HOST_MANAGE_TENANTS]).model_dump(mode="json"),
    )

    assert response.status_code == 403
    assert (await Role.get(role.id)).permissions != [Permission.HOST_MANAGE_TENANTS]


async def test_host_admin_can_grant_host_permissions(client: AsyncClient):
    role = await Role(name="custom", description=None).insert()

    response = await client.put(
        f"/roles/{role.id}",
        json=UpdateRoleDto(name="custom", permissions=[Permission.HOST_MANAGE_TENANTS]).model_dump(mode="json"),
    )

    assert response.status_code == 200


@pytest.mark.parametrize("method, path, body", [
    ("post", "/tenants/{id}/update_dns", {"custom_domain": "evil.example.com"}),
    ("get", "/tenants/{id}/check_dns", None),
    ("patch", "/tenants/{id}/activate_trial_plan", None),
])
async def test_tenant_admin_can_not_manage_another_tenant(client: AsyncClient, act_as, method, path, body):
    victim = await seed_tenant("victim")
    attacker = await seed_tenant("attacker")
    act_as(make_user([Permission.FULL_ACCESS], tenant_id=str(attacker.id)))

    kwargs = {"json": body} if body else {}
    response = await getattr(client, method)(path.format(id=victim.id), **kwargs)

    assert response.status_code == 403


async def test_tenant_admin_manages_own_domain_but_can_not_reactivate_itself(client: AsyncClient, act_as):
    tenant = await seed_tenant()
    await tenant.set({"is_active": False})
    act_as(make_user([Permission.MANAGE_TENANT_SETTINGS], tenant_id=str(tenant.id)))

    with patch("api.interfaces.api_controllers.tenant_endpoint.handle_tenant_dns_update"):
        response = await client.post(
            f"/tenants/{tenant.id}/update_dns",
            json={"custom_domain": "app.example.com", "is_active": True},
        )

    assert response.status_code == 202
    updated = await type(tenant).get(tenant.id)
    assert updated.custom_domain == "app.example.com"
    assert updated.is_active is False


async def test_guest_can_not_activate_a_trial(client: AsyncClient, act_as):
    tenant = await seed_tenant()
    act_as(make_user([Permission.USER_VIEW_ONLY], tenant_id=str(tenant.id)))

    response = await client.patch(f"/tenants/{tenant.id}/activate_trial_plan")

    assert response.status_code == 403
