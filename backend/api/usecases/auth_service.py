from fastapi_mail import MessageType
from pydantic import EmailStr
from api.common.dtos.token_dto import ActivationTokenPayloadDto, RefreshTokenPayloadDto, TokenPayloadDto, TokenRefreshRequestDto, TokenSetDto
from api.common.exceptions import ForbiddenException, InvalidOperationException, UnauthorizedException
from api.common.security import verify_password
from api.common.utils import get_logger, get_utc_now, is_tenancy_enabled, get_email_sharing_link
from api.core.exceptions import TenantNotFoundException
from api.domain.dtos.login_dto import LoginRequestDto
from api.domain.dtos.role_dto import RoleDto
from api.domain.dtos.tenant_dto import CreateTenantDto
from api.domain.dtos.user_dto import CreateUserDto, UserActivationRequestDto, UserResendActivationEmailRequestDto
from api.domain.entities.tenant import validate_subdomain
from api.domain.interfaces.email_service import IEmailService
from api.infrastructure.security.jwt_token_service import JwtTokenService
from api.interfaces.email_templates.password_reset_email_template_html import password_reset_email_template_html
from api.interfaces.email_templates.notify_password_changes_template_html import notify_password_change_template_html
from api.interfaces.email_templates.activation_template_html import activation_template_html
from api.usecases.role_service import RoleService
from api.usecases.tenant_service import TenantService
from api.usecases.user_service import UserService
from typing import Callable

logger = get_logger(__name__)

class AuthService:
    def __init__(self, 
            user_service: UserService,
            tenant_service: TenantService,
            role_service: RoleService,
            jwt_token_service: JwtTokenService,
            email_service: IEmailService
        ):
        self.user_service: UserService = user_service
        self.tenant_service: TenantService = tenant_service
        self.role_service: RoleService = role_service
        self.jwt_token_service: JwtTokenService = jwt_token_service
        self.email_service: IEmailService = email_service
        logger.info("Initialized.")
        print(self.email_service, "email service in auth service")

    async def login(self, req: LoginRequestDto) -> TokenSetDto:
        user = await self.user_service.find_by_email(email=req.email)
        if verify_password(req.password, user.password) is False:
            raise UnauthorizedException("Authentication failed. Please check your credentials.")


        role = await self.role_service.get_role_by_id(role_id=user.role_id)
        role_doc = await role.to_serializable_dict()    
        payload = TokenPayloadDto(
                sub=user.id,
                email=user.email,
                is_active=user.is_active,
                activated_at=user.activated_at,
                role=RoleDto(**role_doc) if role_doc is not None else None,
                tenant_id=user.tenant_id
            )
        return await self.jwt_token_service.generate_tokens(payload)
    

    async def register(self, new_user: CreateUserDto, cb: Callable) -> None:

        if is_tenancy_enabled() is False:
            new_user.tenant_id = None
            await self.user_service.create_user(user_data=new_user)
            logger.info("New user registered in single-tenant mode.")
            return

        tenant = None
        

        if new_user.tenant_id is None or validate_subdomain(new_user.sub_domain) is not None:
            try:
                tenant = await self.tenant_service.find_by_subdomain(subdomain=new_user.sub_domain)
                if tenant is not None:
                    raise InvalidOperationException(f"Subdomain '{new_user.sub_domain}' is already taken.")
            except TenantNotFoundException as tnfe:
                logger.warning(f"Tenant not found for subdomain '{new_user.sub_domain}': {tnfe} - Proceeding to create new tenant.")
                create_new_tenant = CreateTenantDto(
                    name=new_user.sub_domain.split('.')[0],
                    subdomain=new_user.sub_domain,
                    admin_email=new_user.email,
                    admin_password=new_user.password,
                    first_name=new_user.first_name,
                    last_name=new_user.last_name,
                    gender=new_user.gender,
                )
                newly_created_tenant_id = await self.tenant_service.create_tenant(tenant_data=create_new_tenant)
                logger.info(f"New tenant created with ID: {newly_created_tenant_id} for subdomain '{new_user.sub_domain}' and user creation will be procssed...")
                cb(newly_created_tenant_id)

    
    async def refresh_token(self, token: TokenRefreshRequestDto) -> TokenSetDto:
        """
            Refresh the access token using the provided refresh token.
            On success, returns a new TokenSetDto containing the new access and refresh tokens.
            Raises UnauthorizedException if the refresh token is invalid or expired.
        """
        refresh_token_payload: RefreshTokenPayloadDto = await self.jwt_token_service.decode_token(token=token.refresh_token, type="refresh_token")

        if refresh_token_payload is None:
            raise UnauthorizedException("Invalid refresh token")
        
        user = await self.user_service.get_user_by_id(user_id=str(refresh_token_payload.sub))
        role = await self.role_service.get_role_by_id(role_id=user.role_id)
        role_doc = await role.to_serializable_dict()    
        payload = TokenPayloadDto(
            sub=user.id,
            email=user.email,
            is_active=user.is_active,
            activated_at=user.activated_at,
            role=RoleDto(**role_doc) if role_doc is not None else None,
            tenant_id=user.tenant_id
        )
        return await self.jwt_token_service.generate_tokens(payload)


            
    async def initate_password_reset(self, email: EmailStr) -> None:
        reset_data = await self.user_service.request_password_reset(email)
        data = ActivationTokenPayloadDto(
            user_id=str(reset_data.user_id),
            email=email,
            type="password_reset_confirmation",
            jwt_secret=reset_data.token_secret,
            tenant_id=str(reset_data.tenant_id)
        )
        token = await self.jwt_token_service.encode_activation_token(data)
        link = get_email_sharing_link(token=token, user_id=str(reset_data.user_id), type=data.type)
        html = password_reset_email_template_html(user_first_name=reset_data.first_name, password_reset_link=link)
        await self.email_service.send_email(
            to=email,
            subject="Password Reset Request",
            body=html,
            type=MessageType.html
        )
        logger.info(f"Password reset initiated for user {reset_data.user_id} ({email})")
            

    async def change_password(self, new_password: str, token: str, user_id: str) -> None:
        reset_data = await self.user_service.retrieve_password_reset_data_by_user_id(user_id=user_id)
        if reset_data is None:
            raise InvalidOperationException("Invalid or expired password reset token.")
        payload = await self.jwt_token_service.verify_password_reset_token(token=token, jwt_secret=reset_data.token_secret)
        if payload.user_id != user_id:
            raise InvalidOperationException("Invalid password reset token.")
        await self.user_service.update_user_password(user_id=user_id, new_password=new_password)
        result = await self.user_service.clear_password_reset_data_by_user_id(user_id=user_id)
        if result is True:
            logger.info(f"Password reset successful for user {user_id}. Cleared reset data.")
            html = notify_password_change_template_html(user_first_name=reset_data.first_name)
            await self.email_service.send_email(
                to=payload.email,
                subject="Your Password Has Been Changed",
                body=html,
                type=MessageType.html
            )
        

    async def send_activation_email(self, payload: UserResendActivationEmailRequestDto) -> None:
        user = await self.user_service.find_by_email(email=payload.email)
        if user.is_active:
            raise InvalidOperationException("User is already active.")
        activation_token = await self.jwt_token_service.encode_activation_token(payload=ActivationTokenPayloadDto(
            user_id=str(payload.id),
            email=payload.email,
            type="activation",
            tenant_id=payload.tenant_id
        ))
        link = get_email_sharing_link(token=activation_token, user_id=payload.id, type="activation")
        html = activation_template_html(user_first_name=payload.first_name, activation_link=link)
        await self.email_service.send_email(
            to=payload.email,
            subject="Account Activation",
            body=html,
            type=MessageType.html
        )
        logger.info(f"Activation email sent to {payload.email}")


    async def activate_account(self, req: UserActivationRequestDto) -> None:
        payload = await self.jwt_token_service.verify_activation_token(token=req.token)
        user = await self.user_service.get_user_by_id(user_id=payload.user_id)
      
    
        if user.is_active:
            raise InvalidOperationException("User is already active.")
        
        if user.email != payload.email:
            raise ForbiddenException("Oh no, You are not allowed to perform this operation.")
        
        user.is_active = True
        user.activated_at = get_utc_now()
        await user.save()
        logger.info(f"User {user.id} ({user.email}) has been activated.")
        

    async def change_email(self, current_email: EmailStr, new_email: EmailStr) -> None:
        user = await self.user_service.find_by_email(email=current_email)
        user.email = new_email
        await user.save()
        logger.info(f"User {user.id} changed email from {current_email} to {new_email}.")