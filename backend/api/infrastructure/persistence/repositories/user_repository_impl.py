from typing import Optional

from beanie import PydanticObjectId
from api.domain.dtos.user_dto import CreateUserDto, UpdateUserDto, UserListDto
from api.domain.entities.user import User
from api.common.base_repository import BaseRepository
from api.interfaces.middlewares.tenant_middleware import get_tenant_id

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def list (self, skip: int = 0, limit: int = 10) -> UserListDto:
        docs = await self.model.find_all().skip(skip).limit(limit).to_list()
        total = await self.model.count()
        return UserListDto(
            users=[await doc.to_serializable_dict() for doc in docs],
            skip=skip,
            limit=limit,
            total=total,
            hasPrevious=skip > 0,
            hasNext=skip + limit < total
        )

    async def create(
            self, 
            data: CreateUserDto,
        ) -> PydanticObjectId | None:
        new_user = User(
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            gender=data.gender,
            password=data.password,
            is_active=False,
            tenant_id=data.tenant_id
        )
        result = await super().create(new_user.model_dump())
        return result.id

    async def update(self, user_id: str, data: UpdateUserDto) -> Optional[User]:
        print("Updating User ID:", user_id)
        print("Update Data:", data) 
        updated_user = await super().update(id=user_id, data=data.model_dump(exclude_unset=True))
        print("Updated User:", updated_user)
        if updated_user:
            return updated_user
        return None
