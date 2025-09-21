import pytest
from httpx import AsyncClient
from api.common.enums.gender import Gender
from api.common.exceptions import InvalidOperationException
from api.core.exceptions import InvalidSubdomainException
from api.domain.dtos.tenant_dto import CreateTenantDto, CreateTenantResponseDto, TenantDto, TenantListDto
from api.domain.dtos.user_dto import CreateUserResponseDto


async def create_tenant(client: AsyncClient) -> CreateTenantResponseDto:
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
    assert data.hasNext == False
    assert data.hasPrevious == False
    assert data.skip == 0
    assert data.limit == 10


@pytest.mark.asyncio
async def test_create_tenant_as_host(client: AsyncClient):
    """
        Create a new tenant:
    """
    new_tenant_response = await create_tenant(client)

    # Verify the user was created by listing users again
    response = await client.get("/tenants/?skip=0&limit=10")
    assert response.status_code == 200
    data = TenantListDto.model_validate(response.json())
    assert data.total == 1
    assert data.tenants[0].id == new_tenant_response.id



@pytest.mark.asyncio
async def test_search_tenant_by_subdomain_as_host(client: AsyncClient):
    """
        Get a tenant by subdomain:
    """
    new_tenant_response = await create_tenant(client)
    response = await client.get(f"/tenants/search_by_subdomain/test.fsrapp.com")
    assert response.status_code == 200
    data = TenantDto.model_validate(response.json())
    assert data.name == "test"
    assert data.subdomain == "test.fsrapp.com"
    assert data.id == new_tenant_response.id




@pytest.mark.asyncio
async def test_delete_tenant_by_id_from_host(client: AsyncClient):
    """
        Delete a tenant by ID:
    """
    new_tenant_response = await create_tenant(client)
    response = await client.delete(f"/tenants/{new_tenant_response.id}")
    assert response.status_code == 202



@pytest.mark.asyncio
async def test_get_nonexistent_tenant_by_name_as_host(client: AsyncClient):
    """
        Attempt to get a non-existent tenant by name:
    """
    response = await client.get("/tenants/search_by_name/nonexistent-tenant")
    assert response.status_code == 404
    assert response.json()["error"] == "Tenant with identifier nonexistent-tenant not found."


@pytest.mark.asyncio
async def test_list_of_tenants_paginated_in_host(client: AsyncClient):
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
        assert response.status_code == 201
    # Create a single user and return the response

    # Verify the user was created by listing users again
    response = await client.get("/tenants/?skip=0&limit=1")
    assert response.status_code == 200
    data = TenantListDto.model_validate(response.json())
    assert data.total == 3
    assert len(data.tenants) == 1
    assert data.hasNext == True
    assert data.hasPrevious == False
    assert data.skip == 0
    assert data.limit == 1

    response = await client.get("/tenants/?skip=1&limit=1")
    assert response.status_code == 200
    data = TenantListDto.model_validate(response.json())
    assert data.total == 3
    assert len(data.tenants) == 1
    assert data.hasNext == True
    assert data.hasPrevious == True
    assert data.skip == 1
    assert data.limit == 1

    response = await client.get("/tenants/?skip=2&limit=1")
    assert response.status_code == 200
    data = TenantListDto.model_validate(response.json())
    assert data.total == 3
    assert len(data.tenants) == 1
    assert data.hasNext == False
    assert data.hasPrevious == True
    assert data.skip == 2
    assert data.limit == 1


@pytest.mark.asyncio
async def test_validate_subdomain_when_tenant_creation(client: AsyncClient):
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
async def test_validate_password_when_tenant_creation(client: AsyncClient):
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
