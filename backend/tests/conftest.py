# tests/conftest.py
import os

# Settings are read when `api` is imported, so these have to be set first. Everything is
# forced rather than defaulted: a developer's .env must never point the tests at real
# databases or real credentials, because the fixtures below drop what they use.
TEST_DB_NAME = "api_test_db"
TEST_REDIS_URI = os.environ.get("TEST_REDIS_URI", "redis://localhost:6372/15")

os.environ.update({
    "MONGO_URI": os.environ.get("TEST_MONGO_URI", "mongodb://localhost:27012"),
    "MONGO_DB_NAME": TEST_DB_NAME,
    "REDIS_URI": TEST_REDIS_URI,
    "CELERY_BROKER_URL": TEST_REDIS_URI,
    "CELERY_RESULT_BACKEND": TEST_REDIS_URI,
    "FASTAPI_ENV": "test",
    "MULTI_TENANCY_STRATEGY": "header",
    "HOST_MAIN_DOMAIN": "fsrapp.com",
    "JWT_SECRET": "test-jwt-secret-that-is-long-enough-for-hs256",
    "REFRESH_TOKEN_SECRET": "test-refresh-secret-that-is-long-enough-for-hs512-signatures-1234",
    "SMTP_USER": "",
    "SMTP_PASSWORD": "",
    "SMTP_HOST": "localhost",
    "SMTP_PORT": "1",
    "SMTP_MAIL_FROM": "noreply@example.com",
    "COOLIFY_ENABLED": "false",
    "COOLIFY_API_URL": "http://coolify.invalid",
    "COOLIFY_API_KEY": "test",
    "COOLIFY_APPLICATION_ID": "test",
    "AWS_ACCESS_KEY_ID": "test",
    "AWS_SECRET_ACCESS_KEY": "test",
    "STRIPE_API_KEY": "sk_test_key",
    "STRIPE_PUBLISHABLE_KEY": "pk_test_key",
    "STRIPE_SECRET_KEY": "sk_test_key",
    "STRIPE_WEBHOOK_SECRET": "whsec_test",
})

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from api import app
from api.domain.enum.permission import Permission
from api.infrastructure.externals.redis_client import redis_client
from api.infrastructure.externals.smtp_email import SmtpEmail
from api.infrastructure.persistence.mongodb import mongo_client
from api.infrastructure.security.current_user import get_current_user
from tests.factories import make_user


@pytest.fixture(autouse=True)
async def test_app():
    await mongo_client.init_db(TEST_DB_NAME, is_tenant=False)

    # Tests act as a host admin unless they say otherwise, see `act_as`.
    admin = make_user([Permission.FULL_ACCESS, Permission.HOST_MANAGE_TENANTS], email="admin@example.com")
    app.dependency_overrides[get_current_user] = lambda: admin
    yield app
    app.dependency_overrides.clear()
    await mongo_client.drop()
    await redis_client.flushdb()


@pytest.fixture
def act_as(test_app):
    """Run the rest of the test as the given user."""
    def _act_as(user):
        test_app.dependency_overrides[get_current_user] = lambda: user
    return _act_as


@pytest.fixture
async def client(test_app):
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test/api/v1"
    ) as client:
        yield client


@pytest.fixture
async def real_auth_client(test_app):
    """A client that goes through the real authentication instead of the mocked admin."""
    test_app.dependency_overrides.pop(get_current_user, None)
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test/api/v1"
    ) as client:
        yield client


@pytest.fixture(autouse=True)
def sent_emails():
    """Nothing leaves the test run. Inspect `.await_args_list` for what would have been sent."""
    with patch.object(SmtpEmail, "send_email", new_callable=AsyncMock) as send_email:
        yield send_email


@pytest.fixture
async def tenant_databases():
    """Collects tenant ids, whose databases are dropped after the test."""
    tenant_ids: list[str] = []
    yield tenant_ids
    for tenant_id in tenant_ids:
        await mongo_client.client.drop_database(f"tenant_{tenant_id}")
