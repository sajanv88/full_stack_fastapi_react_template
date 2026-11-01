from unittest.mock import patch

import pytest
from beanie import PydanticObjectId
from httpx import AsyncClient

from api.domain.entities.role import Role
from api.domain.entities.user import User
from api.domain.enum.feature import Feature
from api.domain.enum.permission import Permission
from api.domain.security.feature_access_management import check_feature_access
from tests.factories import make_user, seed_tenant, seed_user

SELF_SERVICE = [Permission.USER_SELF_READ_AND_WRITE_ONLY]


async def test_user_can_edit_own_profile(client: AsyncClient, act_as):
    user = await seed_user()
    act_as(make_user(SELF_SERVICE, user_id=str(user.id)))

    response = await client.put(f"/users/{user.id}", json={"first_name": "Renamed"})

    assert response.status_code == 200
    assert response.json()["first_name"] == "Renamed"


async def test_user_can_not_edit_another_user(client: AsyncClient, act_as):
    """Regression: self access compared the caller with itself, so it passed for every target."""
    victim = await seed_user(email="victim@example.com")
    act_as(make_user(SELF_SERVICE))

    response = await client.put(f"/users/{victim.id}", json={"first_name": "Hacked"})

    assert response.status_code == 403
    assert (await User.get(victim.id)).first_name == "Test"


async def test_user_can_not_replace_another_users_picture(client: AsyncClient, act_as):
    victim = await seed_user(email="victim@example.com")
    act_as(make_user(SELF_SERVICE))

    response = await client.put(
        f"/users/{victim.id}/update_profile_picture",
        files={"file": ("a.png", b"png", "image/png")},
    )

    assert response.status_code == 403


async def test_self_service_alone_can_not_read_another_user(client: AsyncClient, act_as):
    victim = await seed_user(email="victim@example.com")
    act_as(make_user(SELF_SERVICE))

    response = await client.get(f"/users/{victim.id}")

    assert response.status_code == 403


async def test_viewer_can_read_users_they_can_already_list(client: AsyncClient, act_as):
    other = await seed_user(email="other@example.com")
    act_as(make_user([Permission.USER_VIEW_ONLY]))

    response = await client.get(f"/users/{other.id}")

    assert response.status_code == 200


async def test_user_can_not_promote_themselves(client: AsyncClient, act_as):
    """Regression: PUT /users/{id} applied role_id, so anyone could become admin."""
    user = await seed_user()
    admin_role = await Role(name="Admin", description=None, permissions=[Permission.FULL_ACCESS]).insert()
    act_as(make_user(SELF_SERVICE, user_id=str(user.id)))

    response = await client.put(f"/users/{user.id}", json={"role_id": str(admin_role.id)})

    assert response.status_code == 403
    assert (await User.get(user.id)).role_id == user.role_id


async def test_sending_the_unchanged_role_is_not_a_privilege_change(client: AsyncClient, act_as):
    user = await seed_user()
    act_as(make_user(SELF_SERVICE, user_id=str(user.id)))

    response = await client.put(f"/users/{user.id}", json={"role_id": str(user.role_id), "last_name": "New"})

    assert response.status_code == 200


async def test_role_assignment_is_stored_as_an_object_id(client: AsyncClient):
    """Regression: role_id was written as a string, which broke the role-in-use check."""
    user = await seed_user()
    role = await Role(name="Other", description=None).insert()

    response = await client.put(f"/users/{user.id}", json={"role_id": str(role.id)})

    assert response.status_code == 200
    assert await User.find({"role_id": role.id}).count() == 1


async def test_assigning_a_missing_role_is_rejected(client: AsyncClient):
    """A user pointing at a missing role can't log in anymore."""
    user = await seed_user()

    response = await client.patch(f"/users/{user.id}/assign_role", json={"role_id": str(PydanticObjectId())})

    assert response.status_code == 404
    assert (await User.get(user.id)).role_id == user.role_id


@pytest.mark.parametrize("stored_as", [str, PydanticObjectId])
async def test_role_in_use_can_not_be_deleted(client: AsyncClient, stored_as):
    """Regression: the string/ObjectId mismatch let roles be deleted from under their users."""
    role = await Role(name="In use", description=None).insert()
    user = await seed_user()
    await User.get_pymongo_collection().update_one({"_id": user.id}, {"$set": {"role_id": stored_as(role.id)}})

    response = await client.delete(f"/roles/{role.id}")

    assert response.status_code == 406
    assert await Role.get(role.id) is not None


async def test_role_search_treats_the_name_as_text(client: AsyncClient):
    await Role(name="Admin", description=None).insert()

    wildcard = await client.get("/roles/search_by_name", params={"name": ".*"})
    literal = await client.get("/roles/search_by_name", params={"name": "adm"})

    assert wildcard.json() == []
    assert [role["name"] for role in literal.json()] == ["Admin"]


@pytest.mark.parametrize("method, path, body", [
    ("post", "/billing/plans", {"amount": 100, "currency": "eur", "interval": "month", "product_id": "prod_1"}),
    ("patch", "/billing/plans/plan_1", {"active": False}),
    ("delete", "/billing/plans/plan_1", None),
])
async def test_guest_can_not_change_billing_plans(client: AsyncClient, act_as, method, path, body):
    """Regression: these only checked the feature flag, so every tenant user could edit plans."""
    tenant = await seed_tenant()
    act_as(make_user([Permission.USER_VIEW_ONLY], tenant_id=str(tenant.id)))

    kwargs = {"json": body} if body else {}
    response = await getattr(client, method)(path, **kwargs)

    assert response.status_code == 403


async def test_forbidden_is_a_403_with_the_error_contract(client: AsyncClient, act_as):
    act_as(make_user([]))

    response = await client.get("/users/")

    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["error"]
    assert response.json()["code"] == 403


async def test_features_do_not_lock_users_out_without_tenancy():
    check = check_feature_access(Feature.CHAT)
    with patch("api.domain.security.feature_access_management.is_tenancy_enabled", return_value=False):
        assert await check(request=None, currentUser=make_user([Permission.USER_VIEW_ONLY])) is True
