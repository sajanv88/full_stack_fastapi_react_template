from typing import Annotated, List, Optional
from fastapi import  APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.responses import StreamingResponse
from app.models.ai_model import AiModel as ModelsResponse
from pydantic import BaseModel
from app.core.ai import  OllamaChat, OllamaModels
from pydantic import BaseModel

from app.models.user import User
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/ai")
router.tags = ["AI"]

class AIRequest(BaseModel):
    question: str
    model_name: Optional[str] = None

class AIResponse(BaseModel):
    answer: str



@router.get("/models", response_model=List[ModelsResponse])
async def get_models(current_user: Annotated[User, Depends(get_current_user)]):
    return OllamaModels().list_models()


@router.post("/ask")
async def ask_ai(current_user: Annotated[User, Depends(get_current_user)], query: AIRequest):
    print(f"AI Chat Request by user: {current_user['first_name']}, model: {query.model_name}")
    if query.model_name is None or query.model_name.strip() == "":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Model name is required")

    chat = OllamaChat(
        current_user["first_name"],
        query.model_name
    )
    stream = chat.generate_response(query.question)
    return StreamingResponse(stream(), media_type="text/plain")
