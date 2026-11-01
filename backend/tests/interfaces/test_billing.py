from datetime import datetime
import hashlib
import hmac
import json
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import stripe
from beanie import PydanticObjectId
from httpx import AsyncClient

from api.common.tenant_context import reset_active_database
from api.core.config import settings
from api.core.container import get_billing_record_service
from api.domain.entities.stripe_settings import BillingRecord, StripeSettings
from api.domain.enum.permission import Permission
from api.infrastructure.persistence.mongodb import mongo_client
from tests.factories import make_user, seed_tenant

TENANT_ID = "68c302ef6bf7a039b7e9b385"


def invoice_event(event_type: str = "invoice.paid", **invoice_fields) -> str:
    return json.dumps({
        "id": "evt_1",
        "object": "event",
        "type": event_type,
        "data": {"object": {
            "id": "in_1",
            "object": "invoice",
            "status": "paid",
            "currency": "eur",
            "amount_paid": 1000,
            "customer": "cus_1",
            "metadata": {"tenant_id": TENANT_ID},
            "lines": {"object": "list", "data": [{
                "period": {"start": 1700000000, "end": 1702592000},
                "pricing": {"price_details": {"price": "price_1", "product": "prod_1"}},
            }]},
            **invoice_fields,
        }},
    })


def signature(payload: str, secret: str = settings.stripe_webhook_secret) -> str:
    timestamp = int(time.time())
    signed = hmac.new(secret.encode(), f"{timestamp}.{payload}".encode(), hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={signed}"


def post_webhook(client: AsyncClient, payload: str, stripe_signature: str):
    return client.post(
        "/configurations/stripe/webhooks",
        content=payload,
        headers={"stripe-signature": stripe_signature, "content-type": "application/json"},
    )


async def test_stripe_can_reach_the_webhook_without_a_session(real_auth_client: AsyncClient):
    """Regression: the route inherited the user permission check, so every delivery was rejected."""
    payload = invoice_event()

    response = await post_webhook(real_auth_client, payload, signature(payload))

    assert response.status_code == 200
    record = await BillingRecord.find_one()
    assert record.amount == 1000
    assert record.price_id == "price_1"
    assert str(record.tenant_id) == TENANT_ID


async def test_a_redelivered_invoice_is_recorded_once(real_auth_client: AsyncClient):
    payload = invoice_event()

    await post_webhook(real_auth_client, payload, signature(payload))
    await post_webhook(real_auth_client, payload, signature(payload))

    assert await BillingRecord.count() == 1


async def test_invoice_with_empty_optional_fields_is_recorded(real_auth_client: AsyncClient):
    """Regression: None values failed validation of the str -> str metadata."""
    payload = invoice_event(billing_reason=None, hosted_invoice_url=None, invoice_pdf=None, metadata=None)

    response = await post_webhook(real_auth_client, payload, signature(payload))

    assert response.status_code == 200
    assert await BillingRecord.count() == 1


async def test_tenant_webhook_is_verified_with_the_tenants_secret(real_auth_client: AsyncClient, tenant_databases):
    tenant = await seed_tenant()
    tenant_databases.append(str(tenant.id))
    token = await mongo_client.use_database(f"tenant_{tenant.id}", is_tenant=True)
    await StripeSettings(stripe_webhook_secret="whsec_tenant").insert()

    payload = invoice_event()
    headers = {"stripe-signature": signature(payload, secret="whsec_tenant"), "X-Tenant-ID": str(tenant.id)}
    response = await real_auth_client.post("/configurations/stripe/webhooks", content=payload, headers=headers)

    assert response.status_code == 200
    assert await BillingRecord.count() == 1
    reset_active_database(token)


async def test_tenant_webhook_rejects_the_host_secret(real_auth_client: AsyncClient, tenant_databases):
    tenant = await seed_tenant()
    tenant_databases.append(str(tenant.id))
    token = await mongo_client.use_database(f"tenant_{tenant.id}", is_tenant=True)
    await StripeSettings(stripe_webhook_secret="whsec_tenant").insert()
    reset_active_database(token)

    payload = invoice_event()
    headers = {"stripe-signature": signature(payload), "X-Tenant-ID": str(tenant.id)}
    response = await real_auth_client.post("/configurations/stripe/webhooks", content=payload, headers=headers)

    assert response.status_code == 400


async def test_forged_webhook_is_rejected(real_auth_client: AsyncClient):
    """Regression: the handler referenced stripe.error, removed in the installed SDK, so this was a 500."""
    payload = invoice_event()

    response = await post_webhook(real_auth_client, payload, signature(payload, secret="whsec_wrong"))

    assert response.status_code == 400
    assert await BillingRecord.count() == 0


async def test_unhandled_events_are_acknowledged(real_auth_client: AsyncClient):
    """Regression: answering 404 makes Stripe retry and eventually disable the endpoint."""
    payload = invoice_event("customer.created")

    response = await post_webhook(real_auth_client, payload, signature(payload))

    assert response.status_code == 200
    assert response.json() == {"status": "ignored"}


def stripe_session(payment_status: str = "paid") -> MagicMock:
    client = MagicMock()
    client.v1.checkout.sessions.retrieve_async = AsyncMock(return_value=SimpleNamespace(payment_status=payment_status))
    return client


@pytest.fixture
def stripe_paid():
    resolver = get_billing_record_service().stripe_resolver
    with patch.object(resolver, "get_stripe_client", AsyncMock(return_value=stripe_session())):
        yield


async def seed_record(tenant_id: PydanticObjectId, user_id: PydanticObjectId | None = None, session: str = "cs_1") -> BillingRecord:
    return await BillingRecord(
        scope="tenant",
        actor="end_user",
        tenant_id=tenant_id,
        user_id=user_id,
        payment_type="subscription",
        currency="eur",
        stripe_session_id=session,
    ).insert()


async def seed_tenant_record(tenant_id: PydanticObjectId) -> tuple[BillingRecord, object]:
    """Host checkouts carry ?tenant_id=, which routes them to the tenant's database."""
    token = await mongo_client.use_database(f"tenant_{tenant_id}", is_tenant=True)
    return await seed_record(tenant_id), token


async def test_tenant_checkout_success_marks_the_record(client: AsyncClient, act_as, stripe_paid):
    """Regression: the lookup used a field that doesn't exist, so it was a 404 for every payment."""
    tenant = await seed_tenant()
    user_id = PydanticObjectId()
    record = await seed_record(tenant.id, user_id)
    act_as(make_user(tenant_id=str(tenant.id), user_id=str(user_id)))

    response = await client.post("/checkouts/tenant/payment/success", params={"session_id": "cs_1"})

    assert response.status_code == 202
    assert (await BillingRecord.get(record.id)).status == "succeeded"
    # The update used to rewrite the whole document, turning its dates into strings.
    stored = await BillingRecord.get_pymongo_collection().find_one({"_id": record.id})
    assert isinstance(stored["created_at"], datetime)


async def test_host_checkout_success_marks_the_record(client: AsyncClient, act_as, stripe_paid, tenant_databases):
    """Regression: an ObjectId was compared with a string, so the tenant check always failed."""
    tenant = await seed_tenant()
    tenant_databases.append(str(tenant.id))
    record, token = await seed_tenant_record(tenant.id)
    act_as(make_user(tenant_id=str(tenant.id)))

    response = await client.post("/checkouts/host/payment/success", params={"session_id": "cs_1", "tenant_id": str(tenant.id)})

    assert response.status_code == 202
    assert (await BillingRecord.get(record.id)).status == "succeeded"
    reset_active_database(token)


async def test_checkout_success_checks_the_owner(client: AsyncClient, act_as, stripe_paid):
    tenant = await seed_tenant()
    record = await seed_record(tenant.id, PydanticObjectId())
    act_as(make_user(tenant_id=str(tenant.id)))

    response = await client.post("/checkouts/tenant/payment/success", params={"session_id": "cs_1"})

    assert response.status_code == 406
    assert (await BillingRecord.get(record.id)).status == "pending"


async def test_tenant_checkout_cancel_marks_pending_records(client: AsyncClient, act_as):
    """Regression: this called list() with a filter, which is a TypeError."""
    tenant = await seed_tenant()
    user_id = PydanticObjectId()
    record = await seed_record(tenant.id, user_id)
    act_as(make_user(tenant_id=str(tenant.id), user_id=str(user_id)))

    response = await client.post("/checkouts/tenant/payment/cancel")

    assert response.status_code == 202
    assert (await BillingRecord.get(record.id)).status == "canceled"


async def test_host_checkout_cancel_marks_pending_records(client: AsyncClient, act_as, tenant_databases):
    tenant = await seed_tenant()
    tenant_databases.append(str(tenant.id))
    record, token = await seed_tenant_record(tenant.id)
    act_as(make_user(tenant_id=str(tenant.id)))

    response = await client.post("/checkouts/host/payment/cancel", params={"tenant_id": str(tenant.id)})

    assert response.status_code == 202
    assert (await BillingRecord.get(record.id)).status == "canceled"
    reset_active_database(token)


async def test_host_checkout_needs_a_tenant(client: AsyncClient, act_as):
    """Regression: this fell through and returned None, a 500 on response validation."""
    act_as(make_user([Permission.HOST_MANAGE_TENANTS]))

    response = await client.post(f"/checkouts/host/{TENANT_ID}/tenant", json={
        "price_id": "price_1", "email": "a@example.com",
    })

    assert response.status_code == 406


async def test_stripe_failures_are_reported_as_a_gateway_error(client: AsyncClient):
    resolver = get_billing_record_service().stripe_resolver
    client_mock = MagicMock()
    client_mock.v1.plans.list_async = AsyncMock(side_effect=stripe.APIConnectionError("Stripe is down"))

    with patch.object(resolver, "get_stripe_client", AsyncMock(return_value=client_mock)):
        response = await client.get("/billing/plans")

    assert response.status_code == 502
    assert response.json()["code"] == 502
