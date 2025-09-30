from api.common.base_repository import BaseRepository
from api.domain.entities.ai import ChatHistoryAI


class ChatHistoryAIRepository(BaseRepository[ChatHistoryAI]):
    def __init__(self) -> None:
        super().__init__(ChatHistoryAI)
    