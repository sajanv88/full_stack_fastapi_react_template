import json
from typing import Optional

from beanie import PydanticObjectId
from api.common.cache_base_repository import CacheBaseRepository
from api.common.utils import get_logger
from api.domain.dtos.user_dto import CreateUserDto, UpdateUserDto, UserListDto
from api.domain.entities.user import User
from api.common.base_repository import BaseRepository

logger = get_logger(__name__)
class UserRepository(BaseRepository[User], CacheBaseRepository):
    def __init__(self):
        super().__init__(User)

    async def list (self, skip: int = 0, limit: int = 10) -> UserListDto:
        key = self.cache_key("list", skip=skip, limit=limit)
        cached = await self.redis.get(key)
        if cached:
            logger.info(f"Cache hit for key: {key}")
            data = json.loads(cached)
            return UserListDto(**data)

        logger.info(f"Cache miss for key: {key}. Querying database.")
        docs = await self.model.find_all().skip(skip).limit(limit).to_list()
        total = await self.model.count()
        result = UserListDto(
            users=[await doc.to_serializable_dict() for doc in docs],
            skip=skip,
            limit=limit,
            total=total,
            hasPrevious=skip > 0,
            hasNext=skip + limit < total
        )
        await self.set_cache(key, result.model_dump_json())
        return result

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
            role_id=data.role_id,
            tenant_id=data.tenant_id
        )
        result = await super().create(new_user.model_dump())
        return result.id

    async def update(self, user_id: str, data: UpdateUserDto) -> Optional[User]:
        updated_user = await super().update(id=user_id, data=data.model_dump(exclude_unset=True))
        if updated_user:
            return updated_user
        logger.warning(f"No user found for the given user id: {user_id}")
        return None
