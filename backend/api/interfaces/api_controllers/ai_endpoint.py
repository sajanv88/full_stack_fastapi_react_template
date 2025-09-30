
from typing import List
from beanie import PydanticObjectId
from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.responses import StreamingResponse

from api.common.dtos.new_session_dto import NewSessionResponseDto
from api.common.exceptions import InvalidOperationException
from api.core.container import get_local_ai_service, get_user_preference_service
from api.domain.dtos.ai_dto import AIAskRequestDto, AIModelInfoDto, AIHistoriesDto
from api.infrastructure.security.current_user import CurrentUser
from api.infrastructure.externals.local_ai_model import OllamaChat, OllamaModels
from api.usecases.local_ai_service import LocalAIService
from api.domain.dtos.ai_dto import AISessionByUserIdDto
from api.usecases.user_preference_service import UserPreferenceService

router = APIRouter(prefix="/ai")
router.tags = ["AI"]

@router.get("/models", response_model=List[AIModelInfoDto])
async def get_models(
    # current_user: CurrentUser
):
    return OllamaModels().list_models()

@router.get("/history", response_model=List[AISessionByUserIdDto])
async def get_history(
    current_user: CurrentUser,
    ai_service: LocalAIService = Depends(get_local_ai_service),
):
    return await ai_service.get_user_sessions(current_user.id)


@router.get("/new_session", response_model=NewSessionResponseDto)
async def create_new_session(current_user: CurrentUser):
    return NewSessionResponseDto(session_id=str(PydanticObjectId()))


@router.get("/sessions/{session_id}", response_model=List[AIHistoriesDto])
async def get_single_session(
    current_user: CurrentUser,
    session_id: str,
    ai_service: LocalAIService = Depends(get_local_ai_service),

):
    return await ai_service.get_histories_by_session_id(current_user.id, session_id)

@router.delete("/sessions/{session_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_session(
    current_user: CurrentUser,
    session_id: str,
    ai_service: LocalAIService = Depends(get_local_ai_service),
):
    await ai_service.delete_session(current_user.id, session_id)
    return status.HTTP_202_ACCEPTED


@router.put("/set_model_preference/{model_name}", status_code=status.HTTP_204_NO_CONTENT)
async def set_preferred_model(
    current_user: CurrentUser,
    model_name: str,
    user_preference: UserPreferenceService = Depends(get_user_preference_service)
):
    if model_name is None or model_name.strip() == "":
        raise InvalidOperationException("Model name cannot be empty")

    await user_preference.set_preferences(user_id=current_user.id, preferences={"model_name": model_name})
    return status.HTTP_204_NO_CONTENT


@router.post("/ask")
async def ask_ai(
    current_user: CurrentUser,
    query: AIAskRequestDto,
    background_tasks: BackgroundTasks,
):
    if query.model_name is None or query.model_name.strip() == "":
        raise InvalidOperationException("Model name cannot be empty")
    
 
    chat = OllamaChat(
        username=current_user.first_name,
        user_id=current_user.id,
        model_name=query.model_name,
        current_session=query.session_id,
        tenant_id=current_user.tenant_id,
    )
    stream = await chat.generate_response(query.question, background_tasks)
    return StreamingResponse(stream(), media_type="text/plain")