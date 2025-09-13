from pydantic import BaseModel
from datetime import datetime

from app.core.utils import PyObjectId


class ChatUniqueSession(BaseModel):
    history_id: PyObjectId
    session_id: PyObjectId
    user_id: PyObjectId
    created_at: datetime