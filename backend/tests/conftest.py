# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport

from api import app
from api.domain.entities.tenant import Tenant
from api.infrastructure.persistence.mongodb import Database
from api.domain.entities.user import User

TEST_MONGO_URI = "mongodb://localhost:27012/test_db"


@pytest.fixture
async def test_app():
    # Initialize test database per test function (same loop as the test)
    db = Database(uri=TEST_MONGO_URI, models=[User, Tenant])
    await db.init_db("api_test_db", is_tenant=False)
    yield app
    await db.drop()


@pytest.fixture
async def client(test_app):
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test/api/v1"
    ) as client:
        yield client
