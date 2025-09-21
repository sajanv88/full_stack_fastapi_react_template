from typing import List

from beanie import PydanticObjectId
from pydantic import EmailStr
from api.core.exceptions import EmailAlreadyExistsException, UserNotFoundException
from api.domain.entities.user import User
from api.domain.dtos.user_dto import CreateUserDto, UpdateUserDto, UserDto, UserListDto
from api.infrastructure.persistence.repositories.user_repository_impl import UserRepository

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def list_users(self, skip: int = 0, limit: int = 10) -> UserListDto:
        return await self.user_repository.list(skip=skip, limit=limit)

    async def find_by_email(self, email: EmailStr) -> User:
        existing = await self.user_repository.single_or_none(email=email)
        if existing is None:
            raise UserNotFoundException(email)
        return existing
    
    async def get_user_by_id(self, user_id: str) -> User:
        existing = await self.user_repository.get(id=user_id)
        if existing is None:
            raise UserNotFoundException(user_id)
        return existing

    async def create_user(self, user_data: CreateUserDto) -> PydanticObjectId:
        existing = await self.user_repository.single_or_none(email=user_data.email)
        if existing is not None:
            raise EmailAlreadyExistsException(user_data.email)
        return await self.user_repository.create(user_data)

    async def update_user(self, user_id: str, user_data: UpdateUserDto) -> User | None:
        existing = await self.user_repository.get(id=user_id)
        if existing is None:
            raise UserNotFoundException(user_id)
        return await self.user_repository.update(user_id=user_id, data=user_data)
     

    async def delete_user(self, user_id: str) -> None:
        if await self.user_repository.delete(id=user_id) is False:
            raise UserNotFoundException(user_id)
        

    async def total_count(self) -> int:
        return await self.user_repository.count()