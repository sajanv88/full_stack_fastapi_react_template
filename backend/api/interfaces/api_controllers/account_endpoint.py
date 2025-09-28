from typing import Annotated
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from api.common.dtos.token_dto import TokenRefreshRequestDto, TokenSetDto
from api.common.dtos.worker_dto import WorkerPayloadDto
from api.common.utils import get_logger
from api.core.container import get_auth_service
from api.domain.dtos.auth_dto import PasswordResetRequestDto, PasswordResetResponseDto
from api.domain.dtos.login_dto import LoginRequestDto
from api.domain.dtos.user_dto import CreateUserDto, UserDto
from api.infrastructure.messaging.celery_worker import handle_post_tenant_creation
from api.infrastructure.security.current_user import get_current_user
from api.interfaces.middlewares.tenant_middleware import get_tenant_id
from api.usecases.auth_service import AuthService

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


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: CreateUserDto,
    auth_service: AuthService = Depends(get_auth_service),
    x_tenant_id: PydanticObjectId | None = Depends(get_tenant_id)
):
    logger.info(f"Register attempt for user: {data.email} x_tenant_id: {x_tenant_id}")

    if x_tenant_id is not None:
        data.tenant_id = x_tenant_id
      
    def process_user_creation(tenant_id: PydanticObjectId):
        logger.info(f"Processing user creation for tenant_id: {tenant_id}")
        data.tenant_id = tenant_id
        payload=WorkerPayloadDto[CreateUserDto](
            label="post-tenant-creation",
            data=data,
            tenant_id=str(tenant_id)
        )
        handle_post_tenant_creation.delay(
            payload=payload.model_dump_json()
        )
        
    await auth_service.register(data, process_user_creation)
    return status.HTTP_201_CREATED
        

@router.get("/me", response_model=UserDto, status_code=status.HTTP_200_OK)
async def read_users_me(
    current_user: Annotated[UserDto, Depends(get_current_user)]
):
    return current_user


@router.post("/refresh", response_model=TokenSetDto, status_code=status.HTTP_200_OK)
async def refresh_token(
    token: TokenRefreshRequestDto,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.refresh_token(token)


@router.post("/password_reset_request", response_model=PasswordResetResponseDto, status_code=status.HTTP_200_OK)
async def password_reset_request(
    request: PasswordResetRequestDto,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        await auth_service.initate_password_reset(request.email)
    except Exception as e:
        logger.error(f"Password reset request for email: {request.email} wasn't successful: {e}")
    finally:
        return PasswordResetResponseDto(message="If the email exists, a password reset link has been sent.")
   