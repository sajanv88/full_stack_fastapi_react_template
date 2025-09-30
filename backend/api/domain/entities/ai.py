from datetime import datetime
from beanie import PydanticObjectId
from pydantic import BaseModel
from api.domain.entities.api_base_model import ApiBaseModel


class ChatSessionAI(ApiBaseModel):
    session_id: PydanticObjectId
    user_id: PydanticObjectId
    history_id: PydanticObjectId



    async def to_serializable_dict(self):
        base_doc = await super().to_serializable_dict()
        return {
            **base_doc,
            "session_id": str(self.session_id),
            "user_id": str(self.user_id), 
            "history_id": str(self.history_id)
        }
    class Settings:
        name = "chat_unique_sessions_ai"


class History(BaseModel):
    uid: str
    query: str
    response: str
    timestamp: datetime

    def to_serializable_dict(self):
        return {
            "uid": self.uid,
            "query": self.query,
            "response": self.response,
            "timestamp": str(self.timestamp)
        }


class ChatHistoryAI(ApiBaseModel):
    histories: list[History]
    async def to_serializable_dict(self):
        base_doc = await super().to_serializable_dict()
        return {
            **base_doc,
            "histories": [history.to_serializable_dict() for history in self.histories]
        }
    class Settings:
        name = "chat_histories_ai"



class AISessions(ChatSessionAI):
    sessions: list[ChatHistoryAI]
    