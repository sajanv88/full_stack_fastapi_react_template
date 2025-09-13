import logging
from typing import Annotated, List, Optional
from fastapi import  APIRouter, HTTPException, Response, status
from fastapi.params import Depends
from fastapi.responses import StreamingResponse
from app.core.db import get_db_reference
from app.models.ai_model import AiModel
from pydantic import BaseModel
from app.core.ai import  OllamaChat, OllamaModels
from pydantic import BaseModel

from app.models.user import User
from app.api.routes.auth import get_current_user
from app.services.ai_history_service import AIHistoryService
from app.services.user_prefernce_service import UserPreferenceService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai")
router.tags = ["AI"]

class AIRequest(BaseModel):
    question: str
    model_name: Optional[str] = None

class AIResponse(BaseModel):
    id: str
    user_id: str
    query: str
    response: str
    timestamp: str 

@router.get("/models", response_model=List[AiModel])
async def get_models(current_user: Annotated[User, Depends(get_current_user)]):
    return OllamaModels().list_models()


@router.get("/history", response_model=List[AIResponse])
async def get_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db = Depends(get_db_reference)
):
    history_service = AIHistoryService(db)
    user_history = await history_service.get_user_history(current_user["id"])
    return [await history_service.serialize(item) for item in user_history]


@router.put("/set_model_preference/{model_name}", status_code=status.HTTP_204_NO_CONTENT)
async def set_preferred_model(
    current_user: Annotated[User, Depends(get_current_user)],
    model_name: str,
    db = Depends(get_db_reference)
):
    if model_name is None or model_name.strip() == "":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Model name is required")
    
    user_preference = UserPreferenceService(db)
    await user_preference.save(user_id=current_user["id"], perferences={"model_name": model_name})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/ask")
async def ask_ai(
    current_user: Annotated[User, Depends(get_current_user)],
    query: AIRequest,
    db = Depends(get_db_reference)
):
    print(f"AI Chat Request by user: {current_user['first_name']}, model: {query.model_name}")
    if query.model_name is None or query.model_name.strip() == "":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Model name is required")
    

    chat = OllamaChat(
        username=current_user["first_name"],
        user_id=current_user["id"],
        model_name=query.model_name,
        db=db
    )
    stream = await chat.generate_response(query.question)
    return StreamingResponse(stream(), media_type="text/plain")


