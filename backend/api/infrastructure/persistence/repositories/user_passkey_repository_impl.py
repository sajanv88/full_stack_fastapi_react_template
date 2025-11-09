from typing import Literal, Optional

from beanie import PydanticObjectId
from api.common.audit_logs_repository import AuditLogRepository
from api.common.base_repository import BaseRepository
from api.common.utils import get_logger
from api.domain.dtos.audit_logs_dto import AuditLogDto
from api.domain.entities.user_passkey import Challenges, UserPasskey
import base64

logger = get_logger(__name__)

class UserPasskeyRepository(BaseRepository[UserPasskey], AuditLogRepository):
    def __init__(self):
        super().__init__(UserPasskey)


class UserPasskeyChallengesRepository(BaseRepository[Challenges], AuditLogRepository):
    def __init__(self):
        super().__init__(Challenges)

    async def save_challenge(self, email: str, challenge: bytes, type: Literal["registration", "authentication"], tenant_id: Optional[PydanticObjectId] = None) -> Challenges:
        """
            Save challenges with current user email, return challenge
        """
        cv = base64.urlsafe_b64encode(challenge).decode("utf-8").rstrip("=")
        logger.debug(f"challenge bytes to a string {cv}")
        data = Challenges(
            email=email,
            challenge=cv,
            type=type,
            tenant_id=tenant_id
        )
        res = await self.create(data=data.model_dump())
        await self.add_audit_log(AuditLogDto(
            action="create",
            entity="UserPasskeyChallenges",
            user_id=email,
            changes={"Info": "Created new challenge for user with type " + type},
            tenant_id=str(tenant_id) if tenant_id else None
        ))
        return res
    
    async def get_challenge(self, email: str, type: Literal["registration", "authentication"]) -> Optional[Challenges]:
        """
            Returns current challenge for the given email if found otherwise, None
        """
        return await self.single_or_none(email=email, type=type)
    

    async def delete_challenge(self, email: str, type: Literal["registration", "authentication"]) -> bool:
        """
            Delete the current challenge for the given email, Returns False if its not found, Otherwise, True
        """
        existing = await self.get_challenge(email=email, type=type)
        if existing is None:
            logger.warning(f"Challenge not found for user {email} with type {type}")
            await self.add_audit_log(AuditLogDto(
                action="delete",
                entity="UserPasskeyChallenges",
                user_id=email,
                changes={"Info": "Attempted to delete non-existing challenge"},
                tenant_id=None
            ))
            return False
        await existing.delete()
        await self.add_audit_log(AuditLogDto(
            action="delete",
            entity="UserPasskeyChallenges",
            user_id=email,
            changes={"Info": "Deleted challenge for user with type " + type},
            tenant_id=str(existing.tenant_id) if existing.tenant_id else None
        ))
        return True

