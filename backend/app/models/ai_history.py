from typing import List
from pydantic import BaseModel
from datetime import datetime



class AIHistory(BaseModel):
    uid: str
    query: str
    response: str
    timestamp: datetime

class AIHistories(BaseModel):
    id: str
    histories: List[AIHistory]