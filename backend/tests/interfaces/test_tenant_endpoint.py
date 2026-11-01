from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient
from api.common.enums.gender import Gender
from api.core.exceptions import InvalidSubdomainException
from api.domain.dtos.tenant_dto import CreateTenantDto, CreateTenantResponseDto, TenantDto, TenantListDto
from api.domain.dtos.user_dto import CreateUserResponseDto

# ------------------------
# Fixture to mock the background tasks, which need a running Celery worker
# ------------------------
@pytest.fixture
def mock_post_tenant_service():
    with patch("api.interfaces.api_controllers.tenant_endpoint.handle_post_tenant_creation") as creation_task,          patch("api.interfaces.api_controllers.tenant_endpoint.handle_post_tenant_deletion"):
        yield creation_task.delay
    
# ------------------------
# Mock Database for tenant tests
# ------------------------
@pytest.fixture
def mock_db():
    with patch("api.infrastructure.persistence.mongodb.Database", new_callable=AsyncMock) as mock_database:
        yield mock_database



async def create_tenant(client: AsyncClient, mock_post_tenant_service) -> CreateTenantResponseDto:
    new_tenant = CreateTenantDto(
       name="test",
       admin_email="test@test.com",
       admin_password="Test@123!",
       first_name="Test",
       last_name="Admin",
       gender=Gender.MALE,
       subdomain="test.fsrapp.com",
    )
    response = await client.post("/tenants/", json=new_tenant.model_dump())
    assert response.status_code == 201
    mock_post_tenant_service.assert_called()

    return CreateUserResponseDto.model_validate(response.json())



@pytest.mark.asyncio
async def test_list_tenants_from_host(client: AsyncClient):
    """
        List all the tenants:
    """
    response = await client.get("/tenants/?skip=0&limit=10")
    print(f"Request URL: {response.url}")
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Body: {response.text}")
    assert response.status_code == 200

    data = TenantListDto.model_validate(response.json())
 
    assert data.tenants == []
    assert data.total == 0
    assert data.has_next == False
    assert data.has_previous == False
    assert data.skip == 0
    assert data.limit == 10


@pytest.mark.asyncio
async def test_create_tenant_as_host(client: AsyncClient, mock_post_tenant_service, mock_db):
    """
        Create a new tenant:
    """
    new_tenant_response = await create_tenant(client, mock_post_tenant_service)

    # Verify the user was created by listing users again
    response = await client.get("/tenants/?skip=0&limit=10")
    assert response.status_code == 200
    data = TenantListDto.model_validate(response.json())
    assert data.total == 1
    assert data.tenants[0].id == new_tenant_response.id



@pytest.mark.asyncio
async def test_search_tenant_by_subdomain_as_host(client: AsyncClient, mock_post_tenant_service, mock_db):
    """
        Get a tenant by subdomain:
    """
    new_tenant_response = await create_tenant(client, mock_post_tenant_service)
    response = await client.get(f"/tenants/search_by_subdomain/test.fsrapp.com")
    assert response.status_code == 200
    data = TenantDto.model_validate(response.json())
    assert data.name == "test"
    assert data.subdomain == "test.fsrapp.com"
    assert data.id == new_tenant_response.id




@pytest.mark.asyncio
async def test_delete_tenant_by_id_from_host(client: AsyncClient, mock_post_tenant_service, mock_db):
    """
        Delete a tenant by ID:
    """
    new_tenant_response = await create_tenant(client, mock_post_tenant_service)
    response = await client.delete(f"/tenants/{new_tenant_response.id}")
    assert response.status_code == 202



@pytest.mark.asyncio
async def test_get_nonexistent_tenant_by_name_as_host(client: AsyncClient,  mock_db):
    """
        Attempt to get a non-existent tenant by name:
    """
    response = await client.get("/tenants/search_by_name/nonexistent-tenant")
    assert response.status_code == 404
    assert response.json()["error"] == "Tenant with identifier nonexistent-tenant not found."


@pytest.mark.asyncio
async def test_list_of_tenants_paginated_in_host(client: AsyncClient, mock_post_tenant_service, mock_db):
    """
        List tenants with pagination:
    """
    for i in range(3):
        new_tenant = CreateTenantDto(
            name=f"test-{i}",
            admin_email=f"test-{i}@test.com",
            admin_password="Test@123!",
            first_name=f"Test-{i}",
            last_name=f"Admin-{i}",
            gender=Gender.MALE,
            subdomain=f"test{i}.fsrapp.com",
        )
        response = await client.post("/tenants/", json=new_tenant.model_dump())
        mock_post_tenant_service.assert_called()
        assert response.status_code == 201
    # Create a single user and return the response

    # Verify the user was created by listing users again
    response = await client.get("/tenants/?skip=0&limit=1")
    assert response.status_code == 200
    data = TenantListDto.model_validate(response.json())
    assert data.total == 3
    assert len(data.tenants) == 1
    assert data.has_next == True
    assert data.has_previous == False
    assert data.skip == 0
    assert data.limit == 1

    response = await client.get("/tenants/?skip=1&limit=1")
    assert response.status_code == 200
    data = TenantListDto.model_validate(response.json())
    assert data.total == 3
    assert len(data.tenants) == 1
    assert data.has_next == True
    assert data.has_previous == True
    assert data.skip == 1
    assert data.limit == 1

    response = await client.get("/tenants/?skip=2&limit=1")
    assert response.status_code == 200
    data = TenantListDto.model_validate(response.json())
    assert data.total == 3
    assert len(data.tenants) == 1
    assert data.has_next == False
    assert data.has_previous == True
    assert data.skip == 2
    assert data.limit == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("name, subdomain", [
    ("test", "other.fsrapp.com"),
    ("other", "test.fsrapp.com"),
])
async def test_tenant_name_and_subdomain_are_unique(client: AsyncClient, mock_post_tenant_service, mock_db, name, subdomain):
    """Regression: a tenant could be created twice, and requests then resolved to the first one."""
    await create_tenant(client, mock_post_tenant_service)

    duplicate = CreateTenantDto(
        name=name,
        admin_email="other@test.com",
        admin_password="Test@123!",
        first_name="Other",
        last_name="Admin",
        gender=Gender.MALE,
        subdomain=subdomain,
    )
    response = await client.post("/tenants/", json=duplicate.model_dump())

    assert response.status_code == 409
    assert (await client.get("/tenants/")).json()["total"] == 1


@pytest.mark.asyncio
async def test_validate_subdomain_when_tenant_creation(client: AsyncClient, mock_db):
    """
        Validate subdomain when creating a tenant:
    """
    with pytest.raises(InvalidSubdomainException) as exc:
        CreateTenantDto(
            name="test",
            admin_email="test@test.com",
            admin_password="Test@123!",
            first_name="Test",
            last_name="Admin",
            gender=Gender.MALE,
            subdomain="test-.fsrapp.com",  # invalid
        )
    assert "invalid format" in str(exc.value)


@pytest.mark.asyncio
async def test_validate_password_when_tenant_creation(client: AsyncClient, mock_db):
    """
        Validate password when creating a tenant:
    """
    new_tenant = CreateTenantDto(
        name="test",
        admin_email="test@test.com",
        admin_password="12",
        first_name="Test",
        last_name="Admin",
        gender=Gender.MALE,
        subdomain="test.fsrapp.com",  # invalid
    )
    response = await client.post("/tenants/", json=new_tenant.model_dump())
    assert response.status_code == 406
    assert response.json()["error"] == "Password must be at least 8 characters long, include uppercase and lowercase letters, a number, and a special character."
