from typing import Annotated
from beanie import PydanticObjectId
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.params import Query
from fastapi.security import OAuth2PasswordRequestForm
from api.common.dtos.token_dto import TokenRefreshRequestDto, TokenSetDto
from api.common.dtos.worker_dto import WorkerPayloadDto
from api.common.exceptions import ForbiddenException, InvalidOperationException
from api.common.utils import get_logger
from api.core.container import get_auth_service
from api.domain.dtos.auth_dto import ChangeEmailConfirmRequestDto, ChangeEmailRequestDto, ChangeEmailResponseDto, MeResponseDto, PasswordResetConfirmRequestDto, PasswordResetRequestDto, PasswordResetResponseDto
from api.domain.dtos.login_dto import LoginRequestDto
from api.domain.dtos.user_dto import CreateUserDto, UserActivationRequestDto, UserDto, UserResendActivationEmailRequestDto
from api.domain.enum.permission import Permission
from api.infrastructure.messaging.celery_worker import handle_post_tenant_creation
from api.infrastructure.security.current_user import CurrentUser
from api.interfaces.middlewares.tenant_middleware import get_tenant_id
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.auth_service import AuthService
from api.core.config import settings
from api.common.dtos.cookies import Cookies

logger = get_logger(__name__)

router = APIRouter(prefix="/account", tags=["Account"])

@router.post("/login", response_model=TokenSetDto, status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    login_request: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service),
    x_tenant_id: str = Depends(get_tenant_id)
):
    logger.info(f"Login attempt for user: {login_request.username} x_tenant_id: {x_tenant_id}")
    token_set: TokenSetDto = await auth_service.login(LoginRequestDto(
        email=login_request.username,
        password=login_request.password
    ))
    
    response.set_cookie(
        key="refresh_token",
        value=token_set.refresh_token,
        httponly=settings.fastapi_env == "production",
        secure=True,
        samesite="lax",
        max_age=settings.refresh_token_expire_days
    )
    return token_set


@router.post("/refresh",  response_model=TokenSetDto, status_code=status.HTTP_200_OK)
async def refresh_token(
    response: Response,
    cookies: Annotated[Cookies, Cookie()],
    auth_service: AuthService = Depends(get_auth_service)
):
    if cookies.refresh_token is None:
        raise ForbiddenException("Refresh token missing!")
    
    token = TokenRefreshRequestDto(refresh_token=cookies.refresh_token)
    
    token_set = await auth_service.refresh_token(token)
    response.set_cookie(
        key="refresh_token",
        value=token_set.refresh_token,
        httponly=settings.fastapi_env == "production",
        secure=True,
        samesite="lax",
        max_age=settings.refresh_token_expire_days
    )
    return token_set

@router.get("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    current_user: CurrentUser,
):
    response.delete_cookie("refresh_token")
    return status.HTTP_200_OK

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
        

@router.get("/me", response_model=MeResponseDto, status_code=status.HTTP_200_OK)
async def read_users_me(
    current_user: CurrentUser
):
    return current_user





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


@router.post("/password_reset_confirmation", response_model=PasswordResetResponseDto)
async def password_reset_confirm(
    request: PasswordResetConfirmRequestDto,
    token: str = Query(..., description="The password reset token"),
    user_id: str = Query(..., description="The user ID associated with the token"),
    tenant_id: str | None = Query(None, description="The tenant ID associated with the user, if applicable"),
    auth_service: AuthService = Depends(get_auth_service)

):
    logger.info(f"Password reset confirmation attempt for user_id: {user_id} with tenant_id: {tenant_id}")
    await auth_service.change_password(
        new_password=request.new_password,
        token=token,
        user_id=user_id
    )
   
    return PasswordResetResponseDto(message="Password has been reset successfully. A notification email has been sent!")

@router.post("/resend_activation_email", status_code=status.HTTP_202_ACCEPTED)
async def resend_activation_email(
    req: UserResendActivationEmailRequestDto,
    auth_service: AuthService = Depends(get_auth_service),
    _bool: bool = Depends(check_permissions_for_current_role(
        required_permissions=[Permission.USER_READ_AND_WRITE_ONLY, Permission.FULL_ACCESS]
    ))
):
    await auth_service.send_activation_email(req)
    return status.HTTP_202_ACCEPTED


@router.post("/activate", status_code=status.HTTP_200_OK)
async def activate_account(
    req: UserActivationRequestDto,
    tenant_id: str | None = Query(None, description="The tenant ID associated with the user, if applicable"),
    auth_service: AuthService = Depends(get_auth_service)
):
    await auth_service.activate_account(req)
    return status.HTTP_200_OK


@router.patch("/change_email_request",  status_code=status.HTTP_202_ACCEPTED)
async def change_email(
    request: ChangeEmailRequestDto,
    current_user: CurrentUser,
    auth_service: AuthService = Depends(get_auth_service)
):
    
    try:
        await auth_service.change_email_request(
            current_email=current_user.email,
            new_email=request.new_email
        )
    finally:
        return status.HTTP_202_ACCEPTED

    
@router.patch("/change_email_confirmation",  status_code=status.HTTP_200_OK, response_model=ChangeEmailResponseDto)
async def change_email_confirmation(
    request: ChangeEmailConfirmRequestDto,
    current_user: CurrentUser,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        await auth_service.change_email_confirmation(
            token=request.token
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=400, detail="Email change confirmation failed.")
    
    return ChangeEmailResponseDto(message="Email changed successfully.")