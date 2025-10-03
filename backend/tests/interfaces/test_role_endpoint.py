import pytest
from httpx import AsyncClient

from api.domain.dtos.role_dto import CreateRoleDto, CreateRoleResponseDto, RoleListDto, UpdateRoleDto, RoleDto
from api.domain.dtos.user_dto import CreateUserDto
from api.domain.enum.permission import Permission


async def create_role(client: AsyncClient) -> CreateRoleResponseDto:
    new_role = CreateRoleDto(
        name="Test Role",
        description="A role for testing purposes",
    )
    response = await client.post("/roles/", json=new_role.model_dump())
    assert response.status_code == 201
    return CreateRoleResponseDto.model_validate(response.json())


@pytest.mark.asyncio
async def test_list_roles_from_host(client: AsyncClient):
    """
        List all the roles:
    """
    response = await client.get("/roles/?skip=0&limit=10")
    print(f"Request URL: {response.url}")
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Body: {response.text}")
    assert response.status_code == 200

    data = RoleListDto.model_validate(response.json())
 
    assert data.roles == []
    assert data.total == 0
    assert data.hasNext == False
    assert data.hasPrevious == False
    assert data.skip == 0
    assert data.limit == 10

@pytest.mark.asyncio
async def test_create_role_in_host(client: AsyncClient):
    """
        Create a new role:
    """
    new_role_response = await create_role(client)

    # Verify the role was created by listing roles again
    response = await client.get("/roles/?skip=0&limit=10")
    assert response.status_code == 200
    data = RoleListDto.model_validate(response.json())
    assert data.total == 1
    assert data.roles[0].id == new_role_response.id

@pytest.mark.asyncio
async def test_get_role_by_id_from_host(client: AsyncClient):
    """
        Get a role by ID:
    """
    new_role_response = await create_role(client)
    response = await client.get(f"/roles/{new_role_response.id}")
    assert response.status_code == 200
    data = RoleDto.model_validate(response.json())
    assert data.name == "Test Role"


@pytest.mark.asyncio
async def test_update_role_by_id_from_host(client: AsyncClient):
    """
        Update a role by ID:
    """
    new_role_response = await create_role(client)
    response = await client.get(f"/roles/{new_role_response.id}")
    assert response.status_code == 200
    data = RoleDto.model_validate(response.json())

    # Update the role's name
    updated_data = UpdateRoleDto(name="Test Role Updated")
    response = await client.put(f"/roles/{new_role_response.id}", json=updated_data.model_dump())
    assert response.status_code == 200
    new_role_updated_data = RoleDto.model_validate(response.json())
    assert new_role_updated_data.name == "Test Role Updated"
    assert data.name != new_role_updated_data.name


@pytest.mark.asyncio
async def test_delete_role_by_id_from_host(client: AsyncClient):
    """
        Delete a role by ID:
    """
    new_role_response = await create_role(client)
    response = await client.delete(f"/roles/{new_role_response.id}")
    assert response.status_code == 202

    # Verify the role was deleted by attempting to get the role again
    response = await client.get(f"/roles/{new_role_response.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_role_by_id_from_host(client: AsyncClient):
    """
        Attempt to get a non-existent role by ID:
    """
    response = await client.get("/roles/68c3031f449ed3590028c778")
    assert response.status_code == 404
    assert response.json()["error"] == "Role with identifier 68c3031f449ed3590028c778 not found."


@pytest.mark.asyncio
async def test_list_of_roles_paginated_in_host(client: AsyncClient):
    """
        List roles with pagination:
    """
    for i in range(3):
        new_role = CreateRoleDto(
          name=f"Test Role {i}",
          description=f"A role for testing purposes {i}",
        )
        response = await client.post("/roles/", json=new_role.model_dump())
        assert response.status_code == 201
    # Create a single user and return the response

    # Verify the user was created by listing users again
    response = await client.get("/roles/?skip=0&limit=1")
    assert response.status_code == 200
    data = RoleListDto.model_validate(response.json())
    assert data.total == 3
    assert len(data.roles) == 1
    assert data.hasNext == True
    assert data.hasPrevious == False
    assert data.skip == 0
    assert data.limit == 1

    response = await client.get("/roles/?skip=1&limit=1")
    assert response.status_code == 200
    data = RoleListDto.model_validate(response.json())
    assert data.total == 3
    assert len(data.roles) == 1
    assert data.hasNext == True
    assert data.hasPrevious == True
    assert data.skip == 1
    assert data.limit == 1

    response = await client.get("/roles/?skip=2&limit=1")
    assert response.status_code == 200
    data = RoleListDto.model_validate(response.json())
    assert data.total == 3
    assert len(data.roles) == 1
    assert data.hasNext == False
    assert data.hasPrevious == True
    assert data.skip == 2
    assert data.limit == 1


@pytest.mark.asyncio
async def test_create_role_with_default_permissions_in_host(client: AsyncClient):
    """
        Create a new role with default permissions:
    """
    new_role_response = await create_role(client)

    # Verify the role was created by listing roles again
    response = await client.get(f"/roles/{new_role_response.id}")
    assert response.status_code == 200
    data = RoleDto.model_validate(response.json())
    assert data.permissions == [Permission.USER_VIEW_ONLY, Permission.ROLE_VIEW_ONLY]