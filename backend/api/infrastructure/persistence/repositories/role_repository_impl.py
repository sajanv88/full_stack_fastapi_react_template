from typing import Optional
from beanie import PydanticObjectId
from api.common.audit_logs_repository import AuditLogRepository
from api.common.base_repository import BaseRepository
from api.common.utils import get_logger
from api.domain.dtos.audit_logs_dto import AuditLogDto
from api.domain.dtos.role_dto import CreateRoleDto, RoleListDto, UpdateRoleDto
from api.domain.entities.role import Role

logger = get_logger(__name__)


class RoleRepository(BaseRepository[Role], AuditLogRepository):
    def __init__(self):
        super().__init__(Role)

    async def list (self, skip: int = 0, limit: int = 10) -> RoleListDto:
        docs = await self.model.find_all().skip(skip).limit(limit).to_list()
        total = await self.model.count()
        result = RoleListDto(
            roles=[await doc.to_serializable_dict() for doc in docs],
            skip=skip,
            limit=limit,
            total=total,
            has_previous=skip > 0,
            has_next=skip + limit < total
        )
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
        await self.add_audit_log(AuditLogDto(
            action="create",
            changes={"Info": f"Create new role with name {data.name} and id {result.id}"},
            entity="Role",
            tenant_id=str(data.tenant_id) if data.tenant_id else None,
            user_id=None # Todo: Need to add a new property in role.. to determine who added it.
        ))
        return result.id


    async def update(self, role_id: str, data: UpdateRoleDto) -> Optional[Role]:
        existing_role = await super().get(role_id)
        updated_role = await super().update(id=role_id, data=data.model_dump(exclude_unset=True))
        if updated_role:
            await self.add_audit_log(AuditLogDto(
                action="update",
                changes={"new": data.model_dump(exclude_unset=True, exclude_none=True), "old": existing_role.model_dump(exclude_none=True, exclude_unset=True)},
                entity="Role",
                tenant_id=str(updated_role.tenant_id) if updated_role.tenant_id else None,
                user_id=None # Todo: Need to add a new property in role.. to determine who updated it.
            ))
            return updated_role
        logger.warning(f"No role found for the given role id: {role_id}")
        await self.add_audit_log(AuditLogDto(
            action="update",
            changes={"Info": f"Attempted to update role with id {role_id}, but it was not found."},
            entity="Role",
            tenant_id=str(existing_role.tenant_id) if existing_role.tenant_id else None,
            user_id=None # Todo: Need to add a new property in role.. to determine who updated it.
        ))
        return None

    async def delete(self, id: str) -> bool:
        existing_role = await super().get(id)
        if not existing_role:
            logger.warning(f"No role found for the given role id: {id}")
            await self.add_audit_log(AuditLogDto(
                action="delete",
                changes={"Info": f"Attempted to delete role with id {id}, but it was not found."},
                entity="Role",
                tenant_id=str(existing_role.tenant_id) if existing_role.tenant_id else None,
                user_id=None # Todo: Need to add a new property in role.. to determine who deleted it.
            ))
            return False
    
        await super().delete(id)
        await self.add_audit_log(AuditLogDto(
            action="delete",
            changes={"Info": f"Deleted role with id {id}"},
            entity="Role",
            tenant_id=str(existing_role.tenant_id) if existing_role.tenant_id else None,
            user_id=None # Todo: Need to add a new property in role.. to determine who deleted it.
        ))
        
        return True
