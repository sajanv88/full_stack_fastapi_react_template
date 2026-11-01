from beanie import PydanticObjectId
from api.common.base_repository import BaseRepository
from api.domain.entities.ai import ChatSessionAI


class ChatSessionAIRepository(BaseRepository[ChatSessionAI]):
    def __init__(self) -> None:
        super().__init__(ChatSessionAI)

    async def is_session_exists(self, session_id: str | None) -> bool:
        if not session_id or not PydanticObjectId.is_valid(session_id):
            return False
        existing = await self.single_or_none(session_id=PydanticObjectId(session_id))
        return existing is not None
    
