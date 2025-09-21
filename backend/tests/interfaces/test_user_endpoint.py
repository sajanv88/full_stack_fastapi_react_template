import pytest
from httpx import AsyncClient
from api.domain.dtos.user_dto import CreateUserResponseDto, UpdateUserDto, UserListDto, CreateUserDto, UserDto
from api.common.enums.gender import Gender


async def create_user(client: AsyncClient) -> CreateUserResponseDto:
    new_user = CreateUserDto(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        gender=Gender.OTHER,
        password="Test@123!"
    )
    response = await client.post("/users/", json=new_user.model_dump())
    assert response.status_code == 201
    return CreateUserResponseDto.model_validate(response.json())


@pytest.mark.asyncio
async def test_list_users_from_host(client: AsyncClient):
    """
        List all the users:
    """
    response = await client.get("/users/?skip=0&limit=10")
    print(f"Request URL: {response.url}")
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Body: {response.text}")
    assert response.status_code == 200

    data = UserListDto.model_validate(response.json())
 
    assert data.users == []
    assert data.total == 0
    assert data.hasNext == False
    assert data.hasPrevious == False
    assert data.skip == 0
    assert data.limit == 10


@pytest.mark.asyncio
async def test_create_user_in_host(client: AsyncClient):
    """
        Create a new user:
    """
    new_user_response = await create_user(client)

    # Verify the user was created by listing users again
    response = await client.get("/users/?skip=0&limit=10")
    assert response.status_code == 200
    data = UserListDto.model_validate(response.json())
    assert data.total == 1
    assert data.users[0].id == new_user_response.id



@pytest.mark.asyncio
async def test_get_user_by_id_from_host(client: AsyncClient):
    """
        Get a user by ID:
    """
    new_user_response = await create_user(client)
    response = await client.get(f"/users/{new_user_response.id}")
    assert response.status_code == 200
    data = UserDto.model_validate(response.json())
    assert data.email == "test@example.com"


@pytest.mark.asyncio
async def test_update_user_by_id_from_host(client: AsyncClient):
    """
        Update a user by ID:
    """
    new_user_response = await create_user(client)
    response = await client.get(f"/users/{new_user_response.id}")
    assert response.status_code == 200
    data = UserDto.model_validate(response.json())

    # Update the user's email
    data.gender = Gender.MALE
    updated_data = UpdateUserDto(**data.model_dump())
    response = await client.put(f"/users/{new_user_response.id}", json=updated_data.model_dump())
    assert response.status_code == 200
    new_user_updated_data = UserDto.model_validate(response.json())
    assert new_user_updated_data.gender == Gender.MALE


@pytest.mark.asyncio
async def test_delete_user_by_id_from_host(client: AsyncClient):
    """
        Delete a user by ID:
    """
    new_user_response = await create_user(client)
    response = await client.delete(f"/users/{new_user_response.id}")
    assert response.status_code == 202

    # Verify the user was deleted by attempting to get the user again
    response = await client.get(f"/users/{new_user_response.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_user_by_id_from_host(client: AsyncClient):
    """
        Attempt to get a non-existent user by ID:
    """
    response = await client.get("/users/68c3031f449ed3590028c778")
    assert response.status_code == 404
    assert response.json()["error"] == "User with identifier 68c3031f449ed3590028c778 not found."


@pytest.mark.asyncio
async def test_list_of_users_paginated_in_host(client: AsyncClient):
    """
        List users with pagination:
    """
    for i in range(3):
        new_user = CreateUserDto(
            email=f"test{i}@example.com",
            first_name=f"Test{i}",
            last_name="User",
            gender=Gender.OTHER,
            password="Test@123!"
        )
        response = await client.post("/users/", json=new_user.model_dump())
        assert response.status_code == 201
    # Create a single user and return the response

    # Verify the user was created by listing users again
    response = await client.get("/users/?skip=0&limit=1")
    assert response.status_code == 200
    data = UserListDto.model_validate(response.json())
    assert data.total == 3
    assert len(data.users) == 1
    assert data.hasNext == True
    assert data.hasPrevious == False
    assert data.skip == 0
    assert data.limit == 1

    response = await client.get("/users/?skip=1&limit=1")
    assert response.status_code == 200
    data = UserListDto.model_validate(response.json())
    assert data.total == 3
    assert len(data.users) == 1
    assert data.hasNext == True
    assert data.hasPrevious == True
    assert data.skip == 1
    assert data.limit == 1

    response = await client.get("/users/?skip=2&limit=1")
    assert response.status_code == 200
    data = UserListDto.model_validate(response.json())
    assert data.total == 3
    assert len(data.users) == 1
    assert data.hasNext == False
    assert data.hasPrevious == True
    assert data.skip == 2
    assert data.limit == 1
