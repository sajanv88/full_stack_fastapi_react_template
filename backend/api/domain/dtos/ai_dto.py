from typing import List, Optional
from pydantic import BaseModel


class AIModelInfoDto(BaseModel):
    name: str
    digest: str
    size: str
    created: str

class AIHistoryDto(BaseModel):
    uid: str
    query: str
    response: str
    timestamp: str
    tenant_id: str | None = None

class AIHistoriesDto(BaseModel):
    id: str
    histories: List[AIHistoryDto]


class AISessionDto(BaseModel):
    id: str
    session_id: str
    created_at: str
    history_id: str
    tenant_id: str | None = None
    user_id: str

class AISessionByUserIdDto(AISessionDto):
    sessions: List[AIHistoriesDto]



class AIAskRequestDto(BaseModel):
    question: str
    model_name: Optional[str] = None
    session_id: Optional[str] = None
