from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from api.common.dtos.token_dto import TokenSetDto
from api.common.utils import get_logger
from api.core.container import get_auth_service
from api.domain.dtos.login_dto import LoginRequestDto
from api.usecases.auth_service import AuthService


logger = get_logger(__name__)

router = APIRouter(prefix="/account", tags=["Account"])

@router.post("/login", response_model=TokenSetDto, status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    login_request: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service)
):
    logger.info(f"Login attempt for user: {request.state.tenant_id}")
    response: TokenSetDto = await auth_service.login(LoginRequestDto(
        email=login_request.username,
        password=login_request.password
    ))
    return response

