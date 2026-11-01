import asyncio
import base64
import re
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

import jwt
import pytest
from fastapi_sso import OpenID
from httpx import AsyncClient

from api.common.exceptions import InvalidOperationException
from api.common.security import verify_password
from api.common.tenant_context import reset_active_database
from api.common.utils import get_utc_now, validate_password
from api.core.config import settings
from api.core.container import get_auth_service, get_passkey_service, get_sso_auth_provider
from api.domain.dtos.audit_logs_dto import AuditLogDto
from api.domain.entities.role import Role
from api.domain.entities.sso_settings import SSOSettings
from api.domain.entities.user import User
from api.domain.entities.user_magic_link import UserMagicLink
from api.domain.entities.user_passkey import Challenges, Credential, UserPasskey
from api.domain.entities.user_password_reset import UserPasswordReset
from api.domain.enum.permission import Permission
from api.domain.enum.role import RoleType
from api.infrastructure.persistence.mongodb import mongo_client
from api.infrastructure.security.passkey_service import decode_base64url
from tests.factories import PASSWORD, make_user, seed_tenant, seed_user


def login(client: AsyncClient, email: str = "user@example.com", password: str = PASSWORD):
    return client.post("/account/login", data={"username": email, "password": password})


def registration(**fields) -> dict:
    return {
        "email": "new@example.com",
        "first_name": "New",
        "last_name": "User",
        "gender": "other",
        "password": PASSWORD,
        **fields,
    }


async def test_login_sets_a_seven_day_refresh_cookie(real_auth_client: AsyncClient):
    await seed_user()

    response = await login(real_auth_client)

    assert response.status_code == 200
    assert "Max-Age=604800" in response.headers["set-cookie"]


async def test_refresh_tokens_expire_in_days_not_millennia(real_auth_client: AsyncClient):
    """Regression: a value in seconds was used as days, so tokens were valid for 1657 years."""
    await seed_user()

    tokens = (await login(real_auth_client)).json()
    payload = jwt.decode(tokens["refresh_token"], settings.refresh_token_secret, algorithms=[settings.refresh_algorithm])

    assert get_utc_now().timestamp() + 6 * 86400 < payload["exp"] < get_utc_now().timestamp() + 8 * 86400
    assert tokens["refresh_token_expires_in"] <= 7 * 86400


async def test_unknown_email_is_indistinguishable_from_a_wrong_password(real_auth_client: AsyncClient):
    await seed_user()

    unknown = await login(real_auth_client, email="nobody@example.com")
    wrong_password = await login(real_auth_client, password="Wrong@123!")

    assert unknown.status_code == wrong_password.status_code == 401
    assert unknown.json() == wrong_password.json()


async def test_inactive_users_can_still_log_in(real_auth_client: AsyncClient):
    """The app relies on this: it shows inactive users a prompt to resend their activation email."""
    await seed_user(is_active=False)

    assert (await login(real_auth_client)).status_code == 200


async def test_repeated_login_attempts_are_rate_limited(real_auth_client: AsyncClient):
    await seed_user()

    attempts = [(await login(real_auth_client, password="Wrong@123!")).status_code for _ in range(11)]

    assert attempts == [401] * 10 + [429]


async def test_rate_limit_is_per_account(real_auth_client: AsyncClient):
    await seed_user()
    await seed_user(email="other@example.com")

    for _ in range(11):
        await login(real_auth_client, password="Wrong@123!")

    assert (await login(real_auth_client, email="other@example.com")).status_code == 200


async def test_me_requires_a_valid_token(real_auth_client: AsyncClient):
    missing = await real_auth_client.get("/account/me")
    invalid = await real_auth_client.get("/account/me", headers={"Authorization": "Bearer garbage"})

    assert missing.status_code == invalid.status_code == 401


async def test_token_of_a_deleted_user_is_unauthorized(real_auth_client: AsyncClient):
    user = await seed_user()
    token = (await login(real_auth_client)).json()["access_token"]
    await user.delete()

    response = await real_auth_client.get("/account/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


async def test_activation_token_is_not_an_access_token(real_auth_client: AsyncClient):
    """It is signed with the same secret, but has a different shape. That used to be a 500."""
    token = jwt.encode({"user_id": "1", "email": "a@b.co", "type": "activation"}, settings.jwt_secret, algorithm="HS256")

    response = await real_auth_client.get("/account/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


async def test_refresh_rotates_tokens(real_auth_client: AsyncClient):
    await seed_user()
    await login(real_auth_client)

    response = await real_auth_client.post("/account/refresh")

    assert response.status_code == 200
    assert "Max-Age=604800" in response.headers["set-cookie"]


async def test_refresh_without_a_cookie_is_a_401(real_auth_client: AsyncClient):
    """worker.ts logs the user out on 401 or 400, any other status would leave a dead session."""
    response = await real_auth_client.post("/account/refresh")

    assert response.status_code == 401


async def test_refresh_of_a_deleted_user_is_a_401(real_auth_client: AsyncClient):
    user = await seed_user()
    await login(real_auth_client)
    await user.delete()

    response = await real_auth_client.post("/account/refresh")

    assert response.status_code == 401


# ---------------------------------------------------------------- password reset

async def request_reset(client: AsyncClient, sent_emails, email: str = "user@example.com") -> tuple[str, str]:
    response = await client.post("/account/password_reset_request", json={"email": email})
    assert response.status_code == 200
    body = sent_emails.await_args.kwargs["body"]
    return re.search(r"user_id=([0-9a-f]{24})", body).group(1), re.search(r"token=([\w.\-]+)", body).group(1)


async def test_password_reset_flow(real_auth_client: AsyncClient, sent_emails):
    """Regression: the endpoint called the service with a missing argument and hid the TypeError."""
    await seed_user()

    user_id, token = await request_reset(real_auth_client, sent_emails)
    response = await real_auth_client.post(
        "/account/password_reset_confirmation",
        params={"token": token, "user_id": user_id},
        json={"new_password": "Changed@123!"},
    )

    assert response.status_code == 200
    assert (await login(real_auth_client, password="Changed@123!")).status_code == 200


async def test_password_reset_works_for_tenant_users(real_auth_client: AsyncClient, sent_emails):
    """Regression: an ObjectId tenant id failed audit log validation."""
    await seed_user(tenant_id="68c302ef6bf7a039b7e9b385")

    await request_reset(real_auth_client, sent_emails)

    assert sent_emails.await_count == 1


async def test_reset_links_ignore_a_forged_host_header(real_auth_client: AsyncClient, sent_emails):
    """The link carries a reset token, so an attacker's Host header must never choose its domain."""
    await seed_user()

    await real_auth_client.post(
        "/account/password_reset_request",
        json={"email": "user@example.com"},
        headers={"Host": "evil.example.com", "X-Forwarded-Host": "evil.example.com"},
    )

    body = sent_emails.await_args.kwargs["body"]
    assert "https://fsrapp.com/password_reset_confirmation" in body
    assert "evil.example.com" not in body


async def test_reset_links_use_the_domain_stored_for_the_tenant(real_auth_client: AsyncClient, sent_emails, tenant_databases):
    tenant = await seed_tenant()
    tenant_databases.append(str(tenant.id))
    token = await mongo_client.use_database(f"tenant_{tenant.id}", is_tenant=True)
    await seed_user(tenant_id=tenant.id)
    reset_active_database(token)

    await real_auth_client.post(
        "/account/password_reset_request",
        json={"email": "user@example.com"},
        headers={"Host": "alpha.fsrapp.com"},
    )

    assert "https://alpha.fsrapp.com/password_reset_confirmation" in sent_emails.await_args.kwargs["body"]


async def test_password_reset_does_not_reveal_unknown_emails(real_auth_client: AsyncClient, sent_emails):
    response = await real_auth_client.post("/account/password_reset_request", json={"email": "nobody@example.com"})

    assert response.status_code == 200
    assert response.json()["message"] == "If the email exists, a password reset link has been sent."
    assert sent_emails.await_count == 0


async def test_password_reset_secret_is_unguessable(real_auth_client: AsyncClient, sent_emails):
    """Regression: it was an ObjectId, which is derived from values anyone can observe."""
    await seed_user()

    await request_reset(real_auth_client, sent_emails)

    assert len((await UserPasswordReset.find_one()).token_secret) >= 43


async def test_password_reset_rejects_weak_passwords(real_auth_client: AsyncClient, sent_emails):
    await seed_user()
    user_id, token = await request_reset(real_auth_client, sent_emails)

    response = await real_auth_client.post(
        "/account/password_reset_confirmation",
        params={"token": token, "user_id": user_id},
        json={"new_password": "weak"},
    )

    assert response.status_code == 406
    assert (await login(real_auth_client)).status_code == 200


async def test_password_reset_requests_are_rate_limited(real_auth_client: AsyncClient):
    statuses = [
        (await real_auth_client.post("/account/password_reset_request", json={"email": "a@example.com"})).status_code
        for _ in range(6)
    ]

    assert statuses == [200] * 5 + [429]


@pytest.mark.parametrize("password", ["aA1!", "aA1!aA1", "alllowercase1!", "ALLUPPERCASE1!", "NoDigits!!", "NoSpecial123"])
def test_password_policy_rejects(password):
    """Regression: the regex never enforced the eight characters its error message promises."""
    with pytest.raises(InvalidOperationException):
        validate_password(password)


@pytest.mark.parametrize("password", [PASSWORD, "Passw0rd!", "With#Other@Symbols1"])
def test_password_policy_accepts(password):
    assert validate_password(password) == password


# ---------------------------------------------------------------- registration

async def test_register_a_new_tenant(real_auth_client: AsyncClient):
    await Role(name=RoleType.GUEST, description=None).insert()

    with patch("api.interfaces.api_controllers.account_endpoint.handle_post_tenant_creation") as task:
        response = await real_auth_client.post("/account/register", json=registration(sub_domain="acme.fsrapp.com"))

    assert response.status_code == 201
    task.delay.assert_called_once()


async def test_register_on_a_taken_subdomain_is_rejected(real_auth_client: AsyncClient):
    """Regression: the error was caught by its own handler, which created a host user instead."""
    await Role(name=RoleType.GUEST, description=None).insert()
    await seed_tenant("acme")

    response = await real_auth_client.post("/account/register", json=registration(sub_domain="acme.fsrapp.com"))

    assert response.status_code == 406
    assert await User.find_one({"email": "new@example.com"}) is None


async def test_register_without_a_subdomain_is_a_client_error(real_auth_client: AsyncClient):
    await Role(name=RoleType.GUEST, description=None).insert()

    response = await real_auth_client.post("/account/register", json=registration())

    assert response.status_code == 406


async def test_register_ignores_a_tenant_id_in_the_body(real_auth_client: AsyncClient):
    await Role(name=RoleType.GUEST, description=None).insert()

    with patch("api.interfaces.api_controllers.account_endpoint.handle_post_tenant_creation"):
        response = await real_auth_client.post("/account/register", json=registration(
            sub_domain="acme.fsrapp.com",
            tenant_id="68c302ef6bf7a039b7e9b385",
        ))

    assert response.status_code == 201
    assert await User.find_one({"email": "new@example.com"}) is None


async def test_register_on_an_existing_tenant_needs_no_subdomain(real_auth_client: AsyncClient, tenant_databases):
    """Regression: this silently created nothing and still answered 201."""
    tenant = await seed_tenant()
    tenant_databases.append(str(tenant.id))
    headers = {"X-Tenant-ID": str(tenant.id)}

    token = await mongo_client.use_database(f"tenant_{tenant.id}", is_tenant=True)
    await Role(name=RoleType.GUEST, description=None).insert()
    reset_active_database(token)

    response = await real_auth_client.post("/account/register", json=registration(), headers=headers)

    assert response.status_code == 201
    token = await mongo_client.use_database(f"tenant_{tenant.id}", is_tenant=True)
    assert await User.find_one({"email": "new@example.com"}) is not None
    reset_active_database(token)


# ---------------------------------------------------------------- account management

async def test_guest_can_resend_their_own_activation(client: AsyncClient, act_as, sent_emails):
    """Regression: this demanded full access, but the prompt is shown to new users, who are guests."""
    user = await seed_user(is_active=False)
    act_as(make_user([Permission.USER_VIEW_ONLY], user_id=str(user.id), email=user.email))

    response = await client.post("/account/resend_activation_email", json={
        "email": user.email, "id": str(user.id), "first_name": user.first_name,
    })

    assert response.status_code == 202
    assert sent_emails.await_count == 1


async def test_guest_can_not_resend_activation_for_someone_else(client: AsyncClient, act_as, sent_emails):
    other = await seed_user(email="other@example.com", is_active=False)
    act_as(make_user([Permission.USER_VIEW_ONLY]))

    response = await client.post("/account/resend_activation_email", json={
        "email": other.email, "id": str(other.id), "first_name": other.first_name,
    })

    assert response.status_code == 403
    assert sent_emails.await_count == 0


async def test_activation_token_is_built_from_the_stored_user(client: AsyncClient, sent_emails):
    """The id in the request is caller supplied, the token must not be signed for it."""
    user = await seed_user(is_active=False)

    await client.post("/account/resend_activation_email", json={
        "email": user.email, "id": "68c302ef6bf7a039b7e9b385", "first_name": "x",
    })

    assert f"user_id={user.id}" in sent_emails.await_args.kwargs["body"]


async def test_email_change_confirmation_goes_to_the_new_address(client: AsyncClient, act_as, sent_emails):
    user = await seed_user()
    act_as(make_user(user_id=str(user.id), email=user.email))

    response = await client.patch("/account/change_email_request", json={"new_email": "new@example.com"})

    assert response.status_code == 202
    assert sent_emails.await_args.kwargs["to"] == "new@example.com"


async def test_email_change_works_for_tenant_users(client: AsyncClient, act_as, sent_emails):
    """Regression: an ObjectId failed token validation, which `finally: return` hid."""
    user = await seed_user(tenant_id="68c302ef6bf7a039b7e9b385")
    act_as(make_user(user_id=str(user.id), email=user.email))

    await client.patch("/account/change_email_request", json={"new_email": "new@example.com"})

    assert sent_emails.await_count == 1


async def test_email_change_does_not_reveal_taken_addresses(client: AsyncClient, act_as, sent_emails):
    user = await seed_user()
    await seed_user(email="taken@example.com")
    act_as(make_user(user_id=str(user.id), email=user.email))

    response = await client.patch("/account/change_email_request", json={"new_email": "taken@example.com"})

    assert response.status_code == 202
    assert sent_emails.await_count == 0


# ---------------------------------------------------------------- magic links

async def test_magic_link_expiry_is_set_per_link():
    """Regression: the default was fixed at import, so the TTL index deleted links within a minute."""
    link = UserMagicLink(user_id="68c302ef6bf7a039b7e9b385", token="t")

    assert abs(link.expires_at - get_utc_now()) < timedelta(seconds=5)


async def test_magic_link_login_flow(real_auth_client: AsyncClient, sent_emails):
    await seed_user()

    response = await real_auth_client.post("/account/email_magic_link_login", json="user@example.com")
    assert response.status_code == 200

    link = await UserMagicLink.find_one()
    validated = await real_auth_client.get(
        "/account/email_magic_link_validate",
        params={"token": link.token, "user_id": str(link.user_id)},
    )

    assert validated.status_code == 200
    assert validated.json()["access_token"]
    assert await UserMagicLink.find_one() is None


async def test_magic_link_for_a_missing_user_is_unauthorized(real_auth_client: AsyncClient):
    """Regression: the error path read variables that only exist when the user was found."""
    with pytest.raises(Exception) as error:
        await get_auth_service().login_with_magic_link(user_id="68c302ef6bf7a039b7e9b385")

    assert type(error.value).__name__ == "UnauthorizedException"


async def test_too_many_magic_links_is_a_429(real_auth_client: AsyncClient):
    await seed_user()

    statuses = [
        (await real_auth_client.post("/account/email_magic_link_login", json="user@example.com")).status_code
        for _ in range(5)
    ]

    assert statuses == [200] * 4 + [429]


# ---------------------------------------------------------------- timestamps

async def test_documents_get_their_own_timestamps():
    """Regression: the defaults were evaluated once at import, stamping everything with the boot time."""
    first = User(first_name="a", last_name="b", email="a@b.co", gender="other", is_active=True, password="x")
    await asyncio.sleep(0.002)
    second = User(first_name="a", last_name="b", email="c@d.co", gender="other", is_active=True, password="x")

    assert first.created_at != second.created_at


async def test_audit_logs_get_their_own_timestamps():
    first = AuditLogDto(entity="User", action="read")
    await asyncio.sleep(0.002)
    second = AuditLogDto(entity="User", action="read")

    assert first.timestamp != second.timestamp


# ---------------------------------------------------------------- passkeys

async def test_passkey_registration_requires_a_session(real_auth_client: AsyncClient):
    """Regression: anyone could add a passkey to any account, then log in with it."""
    await seed_user(email="victim@example.com")

    options = await real_auth_client.post("/account/passkey/register_options", json="victim@example.com")
    complete = await real_auth_client.post("/account/passkey/register", json={
        "email": "victim@example.com", "credential": {},
    })

    assert options.status_code == 401
    assert complete.status_code == 401


async def test_passkey_can_not_be_registered_for_someone_else(client: AsyncClient, act_as):
    act_as(make_user(email="attacker@example.com"))

    response = await client.post("/account/passkey/register_options", json="victim@example.com")

    assert response.status_code == 403


async def test_signed_in_user_can_start_passkey_registration(client: AsyncClient, act_as):
    act_as(make_user(email="user@example.com"))

    response = await client.post("/account/passkey/register_options", json="USER@example.com")

    assert response.status_code == 200
    assert await Challenges.find_one({"email": "user@example.com"}) is not None


def credential(raw_id: bytes, public_key: bytes) -> Credential:
    return Credential(
        credential_id=base64.urlsafe_b64encode(raw_id).decode(),
        public_key=base64.urlsafe_b64encode(public_key).decode(),
        sigin_count=1,
        created_at=get_utc_now(),
    )


async def seed_passkeys() -> None:
    await UserPasskey(user_email="user@example.com", credentials=[
        credential(b"first-id", b"first-key"),
        credential(b"second-id", b"second-key"),
    ]).insert()
    await Challenges(email="user@example.com", type="authentication", challenge="AAAA").insert()


async def test_passkey_login_verifies_against_the_credential_that_was_used():
    """Regression: the first public key was always used, so a second passkey could never log in."""
    await seed_passkeys()
    used_id = base64.urlsafe_b64encode(b"second-id").decode().rstrip("=")
    verified = SimpleNamespace(new_sign_count=5, credential_id=b"second-id")

    with patch("api.infrastructure.security.passkey_service.verify_authentication_response", return_value=verified) as verify:
        await get_passkey_service().complete_auth_login("user@example.com", {"id": used_id, "rawId": used_id})

    assert verify.call_args.kwargs["credential_public_key"] == b"second-key"
    stored = (await UserPasskey.find_one()).credentials
    assert [c.sigin_count for c in stored] == [1, 5]
    assert stored[0].last_used_at is None and stored[1].last_used_at is not None


async def test_passkey_login_rejects_an_unknown_credential():
    await seed_passkeys()

    with pytest.raises(Exception, match="not registered"):
        await get_passkey_service().complete_auth_login("user@example.com", {
            "id": base64.urlsafe_b64encode(b"other").decode().rstrip("="),
        })


async def test_the_newest_passkey_challenge_wins():
    """Regression: a second attempt within the TTL was verified against the first, stale challenge."""
    repository = get_passkey_service().challenges_repo
    await repository.save_challenge("user@example.com", b"old", "authentication")
    await repository.save_challenge("user@example.com", b"new", "authentication")

    challenge = await repository.get_challenge("user@example.com", "authentication")

    assert decode_base64url(challenge.challenge) == b"new"

    await repository.delete_challenge("user@example.com", "authentication")
    assert await repository.get_challenge("user@example.com", "authentication") is None


# ---------------------------------------------------------------- SSO

def openid(email: str = "user@example.com") -> OpenID:
    return OpenID(id="1", email=email, first_name="Sso", last_name="User", provider="google")


async def test_sso_accounts_get_a_random_password():
    """Regression: every SSO account had the password signed_up_via_sso_<provider>."""
    await Role(name=RoleType.GUEST, description=None).insert()

    await get_auth_service().login_with_sso("google", openid(), tenant_id=None)

    user = await User.find_one({"email": "user@example.com"})
    assert user.sso_provider_id == "google"
    assert verify_password("signed_up_via_sso_google", user.password) is False


async def test_existing_sso_accounts_can_not_use_the_old_password(real_auth_client: AsyncClient):
    await seed_user(password="signed_up_via_sso_google", sso_provider_id="google")

    response = await login(real_auth_client, password="signed_up_via_sso_google")

    assert response.status_code == 401


async def test_sso_redirect_is_an_absolute_url_for_the_tenant():
    """Regression: without a scheme the browser resolved it relative to the callback path."""
    tenant = await seed_tenant()
    await SSOSettings(enabled=True, provider="google", client_id="id", client_secret="s", tenant_id=tenant.id).insert()

    url = await get_sso_auth_provider().get_redirect_uri_to_app("google")

    assert url == "http://alpha.fsrapp.com:3000"


async def test_sso_redirect_works_on_the_host():
    await SSOSettings(enabled=True, provider="google", client_id="id", client_secret="s").insert()

    assert await get_sso_auth_provider().get_redirect_uri_to_app("google") == "http://fsrapp.com:3000"


async def test_x_is_a_supported_sso_provider():
    """Regression: `case "x", "twitter"` matches a tuple, so this provider never resolved."""
    settings_doc = SSOSettings(enabled=True, provider="x", client_id="id", client_secret="s")

    sso = await get_sso_auth_provider()._provider_instance("x", settings_doc)

    assert type(sso).__name__ == "TwitterSSO"


async def test_unconfigured_sso_provider_is_a_404(real_auth_client: AsyncClient):
    """Regression: this raised ValueError, a 500."""
    response = await real_auth_client.get("/account/sso/google/login", follow_redirects=False)

    assert response.status_code == 404
