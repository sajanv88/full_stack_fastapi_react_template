from typing import Annotated
from fastapi import  APIRouter
from fastapi.params import Depends
from fastapi.responses import StreamingResponse

from pydantic import BaseModel
from app.core.ai import OllamaChat
from pydantic import BaseModel

from app.models.user import User
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/ai")
router.tags = ["AI"]

class AIRequest(BaseModel):
    question: str

class AIResponse(BaseModel):
    answer: str

@router.post("/ask")
async def ask_ai(current_user: Annotated[User, Depends(get_current_user)], query: AIRequest):
    stream = OllamaChat(current_user["first_name"]).generate_response(query.question)
    return StreamingResponse(stream(), media_type="text/plain")

        