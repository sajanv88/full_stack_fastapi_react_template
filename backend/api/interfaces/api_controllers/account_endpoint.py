from typing import Annotated
from beanie import PydanticObjectId
from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.params import Query
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from api.common.dtos.passkey_rep_dto import HasPasskeysDto
from api.common.dtos.token_dto import TokenRefreshRequestDto, TokenSetDto
from api.common.dtos.worker_dto import WorkerPayloadDto
from api.common.exceptions import ApiBaseException, ForbiddenException, InvalidOperationException
from api.common.utils import get_logger
from api.core.container import get_auth_service, get_email_magic_link_service, get_passkey_service, get_role_service, get_sso_auth_provider, get_user_magic_link_repository
from api.core.exceptions import PassKeyException, UserNotFoundException
from api.domain.dtos.auth_dto import ChangeEmailConfirmRequestDto, ChangeEmailRequestDto, ChangeEmailResponseDto, MagicLinkResponseDto, MeResponseDto, PasswordResetConfirmRequestDto, PasswordResetRequestDto, PasswordResetResponseDto
from api.domain.dtos.login_dto import LoginRequestDto
from api.domain.dtos.user_dto import CreateUserDto, UserActivationRequestDto, UserDto, UserResendActivationEmailRequestDto
from api.domain.entities.sso_settings import SSOProvider
from api.domain.enum.permission import Permission
from api.infrastructure.externals.sso_auth_provider import SSOAuthProvider
from api.infrastructure.messaging.celery_worker import handle_post_tenant_creation
from api.infrastructure.persistence.repositories.user_magic_link_repository_impl import UserMagicLinkRepository
from api.infrastructure.security.current_user import CurrentUser
from api.infrastructure.security.passkey_service import PasskeyService
from api.interfaces.middlewares.tenant_middleware import FrontendHost, get_tenant_id
from api.interfaces.security.role_checker import check_permissions_for_current_role
from api.usecases.auth_service import AuthService
from api.core.config import settings
from api.common.dtos.cookies import Cookies
from api.usecases.magic_link_service import EmailMagicLinkService
from api.usecases.role_service import RoleService
from api.domain.enum.role import RoleType

logger = get_logger(__name__)

router = APIRouter(prefix="/account", tags=["Account"])

@router.post("/login", response_model=TokenSetDto, status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    login_request: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthService = Depends(get_auth_service),
    x_tenant_id: str | None = Depends(get_tenant_id)
):
    logger.info(f"Login attempt for user: {login_request.username} x_tenant_id: {x_tenant_id}")
    token_set: TokenSetDto = await auth_service.login(LoginRequestDto(
        email=login_request.username,
        password=login_request.password
    ))
    
    response.set_cookie(
        key="refresh_token",
        value=token_set.refresh_token,
        httponly=True,
        secure=settings.fastapi_env == "production",
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
        httponly=True,
        secure=settings.fastapi_env == "production",
        samesite="lax",
        max_age=settings.refresh_token_expire_days
    )
    return token_set

@router.get("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    current_user: CurrentUser,
    auth_service: AuthService = Depends(get_auth_service)
):
    response.delete_cookie("refresh_token")
    await auth_service.logout(user_id=str(current_user.id), tenant_id=str(current_user.tenant_id) if current_user.tenant_id else None)
    return status.HTTP_200_OK

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: CreateUserDto,
    auth_service: AuthService = Depends(get_auth_service),
    role_service: RoleService = Depends(get_role_service),
    x_tenant_id: PydanticObjectId | None = Depends(get_tenant_id)
):
    logger.info(f"Register attempt for user: {data.email} x_tenant_id: {x_tenant_id}")
    role_guest = await role_service.find_by_name(name=RoleType.GUEST)

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
    
    data.role_id = role_guest.id
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
    frontend_host: FrontendHost,
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
    frontend_host: FrontendHost,
    auth_service: AuthService = Depends(get_auth_service),
    _bool: bool = Depends(check_permissions_for_current_role(
        required_permissions=[Permission.USER_READ_AND_WRITE_ONLY, Permission.FULL_ACCESS]
    ))
):
    await auth_service.send_activation_email(req, frontend_host)
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
    frontend_host: FrontendHost,
    auth_service: AuthService = Depends(get_auth_service)
):
    
    try:
        await auth_service.change_email_request(
            current_email=current_user.email,
            new_email=request.new_email,
            domain=frontend_host
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



@router.post("/passkey/register_options", status_code=status.HTTP_200_OK)
async def passkey_register_options(
    email: EmailStr = Body(...),
    passkey_service: PasskeyService = Depends(get_passkey_service),
    auth_service: AuthService = Depends(get_auth_service)
):
    user_service = await auth_service.get_user_service()
    user = await user_service.find_by_email(email=email)
    user_dto = await user.to_serializable_dict()
    result = await passkey_service.register_options(user_dto=UserDto(**user_dto))
    
    return result


@router.post("/passkey/register", status_code=status.HTTP_202_ACCEPTED)
async def passkey_register(
    email: EmailStr = Body(...),
    credential: dict = Body(...),
    passkey_service: PasskeyService = Depends(get_passkey_service)
):
    result = await passkey_service.complete_registration(email, credential)
    
    if result is False:
        raise PassKeyException("Passkey registration failed.")
    
    return status.HTTP_202_ACCEPTED
    

@router.post("/passkey/login_options", status_code=status.HTTP_200_OK)
async def passkey_login_options(
    email: EmailStr = Body(...),
    passkey_service: PasskeyService = Depends(get_passkey_service),
    auth_service: AuthService = Depends(get_auth_service)
):
    user_service = await auth_service.get_user_service()
    user = await user_service.find_by_email(email=email)
    user_doc = await user.to_serializable_dict()
    return await passkey_service.auth_login_options(user_dto=UserDto(**user_doc))


@router.post("/passkey/login", status_code=status.HTTP_200_OK, response_model=TokenSetDto)
async def passkey_login(
    response: Response,
    email: EmailStr = Body(...),
    credential: dict = Body(...),
    passkey_service: PasskeyService = Depends(get_passkey_service),
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        result = await passkey_service.complete_auth_login(email, credential)
        if result is False:
            raise PassKeyException("Passkey authentication failed.")
        
        token_set: TokenSetDto = await auth_service.login_with_passkey(email=email)
        
        response.set_cookie(
            key="refresh_token",
            value=token_set.refresh_token,
            httponly=True,
            secure=settings.fastapi_env == "production",
            samesite="lax",
            max_age=settings.refresh_token_expire_days
        )
        return token_set
    except Exception as e:
        logger.error(f"Passkey login failed for email: {email} with error: {e}")
        raise PassKeyException("Passkey authentication failed.") from e
    

@router.post("/passkey/has_passkeys", response_model=HasPasskeysDto, status_code=status.HTTP_200_OK)
async def has_passkeys(
    email: EmailStr = Body(...),
    passkey_service: PasskeyService = Depends(get_passkey_service)
):
    return HasPasskeysDto(has_passkeys=await passkey_service.has_passkeys(email=email))


@router.post("/email_magic_link_login", response_model=MagicLinkResponseDto, status_code=status.HTTP_200_OK)
async def email_magic_link_login(
    email: EmailStr = Body(...),
    magic_link_service: EmailMagicLinkService = Depends(get_email_magic_link_service),
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        user_service = await auth_service.get_user_service()
        user = await user_service.find_by_email(email=email)
        user_doc = await user.to_serializable_dict()
        user_dto = UserDto(**user_doc)
        await magic_link_service.create_magic_link(user_dto)
        return MagicLinkResponseDto(message="If the email exists, a magic link has been sent.")
  
    except Exception as e:
        if isinstance(e, UserNotFoundException):
            logger.error(f"Magic link login request for email: {email} wasn't successful: {e}")
            return MagicLinkResponseDto(message="If the email exists, a magic link has been sent.")
        elif isinstance(e, ApiBaseException):
            raise e
        return MagicLinkResponseDto(message="If the email exists, a magic link has been sent.")
    
       
@router.get("/email_magic_link_validate", response_model=TokenSetDto, status_code=status.HTTP_200_OK)
async def email_magic_link_validate(
    response: Response,
    token: str = Query(..., description="The magic link token"),
    user_id: str = Query(..., description="The user ID associated with the token"),
    tenant_id: str | None = Query(None, description="The tenant ID associated with the user, if applicable"),
    auth_service: AuthService = Depends(get_auth_service),
    magic_link_service: EmailMagicLinkService = Depends(get_email_magic_link_service),
):
    from urllib.parse import unquote
    token = unquote(token)
    logger.info(f"Magic link validation attempt for user_id: {user_id} with tenant_id: {tenant_id}")
    is_valid = await magic_link_service.validate_magic_link(user_id=user_id, token=token)
    if is_valid is False:
        raise ForbiddenException("Invalid or expired magic link.")
    
    token_set: TokenSetDto = await auth_service.login_with_magic_link(user_id=user_id)
    
    response.set_cookie(
        key="refresh_token",
        value=token_set.refresh_token,
        httponly=True,
        secure=settings.fastapi_env == "production",
        samesite="lax",
        max_age=settings.refresh_token_expire_days
    )
    return token_set


@router.get("/sso/{provider_name}/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def sso_provider_login(
    provider_name: SSOProvider,
    sso_auth_provider: SSOAuthProvider = Depends(get_sso_auth_provider)
):
    return await sso_auth_provider.login(provider_name)
    
@router.get("/sso/{provider_name}/callback", status_code=status.HTTP_200_OK)
async def sso_provider_callback(
    provider_name: SSOProvider,
    req: Request,
    sso_auth_provider: SSOAuthProvider = Depends(get_sso_auth_provider)
):
    user = await sso_auth_provider.callback(provider_name, req)
    return user

