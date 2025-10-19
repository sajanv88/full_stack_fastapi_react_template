import json
from typing import Optional
from beanie import PydanticObjectId
from api.common.base_repository import BaseRepository
from api.common.cache_base_repository import CacheBaseRepository
from api.common.utils import get_logger
from api.domain.dtos.role_dto import CreateRoleDto, RoleListDto, UpdateRoleDto
from api.domain.entities.role import Role

logger = get_logger(__name__)


class RoleRepository(BaseRepository[Role], CacheBaseRepository):
    def __init__(self):
        super().__init__(Role)

    async def list (self, skip: int = 0, limit: int = 10) -> RoleListDto:
        key = self.cache_key("list", skip=skip, limit=limit)
        cached = await self.redis.get(key)
        if cached:
            logger.info(f"Cache hit for key: {key}")
            data = json.loads(cached)
            return RoleListDto(**data)

        logger.info(f"Cache miss for key: {key}. Querying database.")
        docs = await self.model.find_all().skip(skip).limit(limit).to_list()
        total = await self.model.count()
        result = RoleListDto(
            roles=[await doc.to_serializable_dict() for doc in docs],
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
            data: CreateRoleDto,
        ) -> PydanticObjectId | None:
        new_role = Role(
           name=data.name,
           description=data.description,
           tenant_id=data.tenant_id
        )
        result = await super().create(new_role.model_dump())
        return result.id


    async def update(self, role_id: str, data: UpdateRoleDto) -> Optional[Role]:
        updated_role = await super().update(id=role_id, data=data.model_dump(exclude_unset=True))
        if updated_role:
            return updated_role
        logger.warning(f"No role found for the given role id: {role_id}")
        return None
