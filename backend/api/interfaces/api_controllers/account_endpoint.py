from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from api.common.dtos.token_dto import TokenSetDto
from api.common.utils import get_logger
from api.core.container import get_auth_service
from api.domain.dtos.login_dto import LoginRequestDto
from api.interfaces.middlewares.tenant_middleware import get_tenant_id
from api.usecases.auth_service import AuthService
from api.common.security import tenant_header

logger = get_logger(__name__)

router = APIRouter(prefix="/account", tags=["Account"])

@router.post("/login", response_model=TokenSetDto, status_code=status.HTTP_200_OK)
async def login(
    login_request: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service),
    x_tenant_id: str = Depends(get_tenant_id)
):
    logger.info(f"Login attempt for user: {login_request.username} x_tenant_id: {x_tenant_id}")
    response: TokenSetDto = await auth_service.login(LoginRequestDto(
        email=login_request.username,
        password=login_request.password
    ))
    return response


