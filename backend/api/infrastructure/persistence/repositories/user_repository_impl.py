from typing import Optional

from beanie import PydanticObjectId
from api.common.exceptions import NotFoundException
from api.common.utils import get_logger
from api.domain.dtos.audit_logs_dto import AuditLogDto
from api.domain.dtos.user_dto import CreateUserDto, UpdateUserDto, UserListDto
from api.domain.entities.user import User
from api.common.base_repository import BaseRepository
from api.common.audit_logs_repository import AuditLogRepository

logger = get_logger(__name__)
class UserRepository(BaseRepository[User], AuditLogRepository):
    def __init__(self):
        super().__init__(User)

    async def list (self, skip: int = 0, limit: int = 10) -> UserListDto:
        docs = await self.model.find_all().skip(skip).limit(limit).to_list()
        total = await self.model.count()
        result = UserListDto(
            users=[await doc.to_serializable_dict() for doc in docs],
            skip=skip,
            limit=limit,
            total=total,
            has_previous=skip > 0,
            has_next=skip + limit < total
        )
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
        d = new_user.model_dump()
        result = await super().create(data=d)
        await self.add_audit_log(AuditLogDto(
            action="create",
            entity="User",
            user_id=str(result.id),
            changes={"new": data.model_dump(exclude={"password", "email"}, exclude_none=True, exclude_unset=True)},
            tenant_id=str(data.tenant_id) if data.tenant_id else None
        ))
        return result.id

    async def update(self, user_id: str, data: UpdateUserDto) -> Optional[User]:
        try:
            exising_user = await self.get(id=user_id)
            if not exising_user:
                raise NotFoundException("User not found")
            updated_user = await super().update(id=user_id, data=data.model_dump(exclude_unset=True))
            if updated_user:
                await self.add_audit_log(AuditLogDto(
                    action="update",
                    entity="User",
                    user_id=str(user_id),
                    changes={
                        "info": f"User with id {user_id} updated.",
                    },
                    tenant_id=str(exising_user.tenant_id) if exising_user.tenant_id else None
                ))
                return updated_user
        except NotFoundException as e:
            logger.error(f"No user found for the given user id: {user_id}")
            await self.add_audit_log(AuditLogDto(
                action="update",
                entity="User",
                user_id=str(user_id),
                changes={"error": f"No user found for the given user id: {user_id}"},
                tenant_id=str(data.tenant_id) if data.tenant_id else None
            ))
            return None

    async def delete(self, user_id: str) -> bool:
        existing_user = await self.get(id=user_id)
        try:
            if not existing_user:
                raise NotFoundException("User not found")

            result = await super().delete(id=user_id)
            if result:
                await self.add_audit_log(AuditLogDto(
                    action="delete",
                    entity="User",
                    user_id=user_id,
                    changes={"info": f"User with id {user_id} deleted."},
                    tenant_id=str(existing_user.tenant_id) if existing_user.tenant_id else None
                ))
            return result
        except NotFoundException as e:
            logger.error(f"No user found for the given user id: {user_id}")
            await self.add_audit_log(AuditLogDto(
                action="delete",
                entity="User",
                user_id=user_id,
                changes={"error": f"No user found for the given user id: {user_id}"},
                tenant_id=str(existing_user.tenant_id) if existing_user and existing_user.tenant_id else None
            ))
            return False
          
       