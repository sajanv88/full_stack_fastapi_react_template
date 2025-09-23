# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport

from api import app
from api.common.enums.gender import Gender
from api.domain.dtos.user_dto import UserDto
from api.domain.entities.role import Role
from api.domain.entities.tenant import Tenant
from api.domain.entities.user_password_reset import UserPasswordReset
from api.domain.entities.user_preference import UserPreference
from api.infrastructure.persistence.mongodb import Database
from api.domain.entities.user import User
from api.infrastructure.security.current_user import get_current_user

TEST_MONGO_URI = "mongodb://localhost:27012/test_db"


@pytest.fixture
async def test_app():
    # Initialize test database per test function (same loop as the test)
    db = Database(uri=TEST_MONGO_URI, models=[User, Tenant, Role, UserPasswordReset, UserPreference])
    await db.init_db("api_test_db", is_tenant=False)

    # Override the get_current_user dependency to return a mocked test user
    async def override_get_current_user():
        return UserDto(
            first_name="Admin",
            last_name="User",
            id="68c302ef6bf7a039b7e9b385",
            email="admin@example.com",
            gender=Gender.OTHER,
            is_active=True,
            role_id="68c302ef6bf7a039b7e9b386",
            created_at="2024-10-01T00:00:00Z",
            updated_at="2024-10-01T00:00:00Z",
        )

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield app
    await db.drop()


@pytest.fixture
async def client(test_app):
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test/api/v1"
    ) as client:
        yield client

