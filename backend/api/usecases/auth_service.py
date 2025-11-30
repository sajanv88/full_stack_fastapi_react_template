from fastapi_mail import MessageType
from fastapi_sso import OpenID
from pydantic import EmailStr
from api.common.dtos.token_dto import ActivationTokenPayloadDto, RefreshTokenPayloadDto, TokenPayloadDto, TokenRefreshRequestDto, TokenSetDto
from api.common.exceptions import ForbiddenException, InvalidOperationException, UnauthorizedException
from api.common.security import verify_password
from api.common.utils import get_logger, get_utc_now, is_tenancy_enabled, get_email_sharing_link
from api.core.exceptions import TenantNotFoundException, UserNotFoundException
from api.domain.dtos.audit_logs_dto import AuditLogDto
from api.domain.dtos.login_dto import LoginRequestDto
from api.domain.dtos.role_dto import RoleDto
from api.domain.dtos.tenant_dto import CreateTenantDto
from api.domain.dtos.user_dto import CreateUserDto, UserActivationRequestDto, UserResendActivationEmailRequestDto
from api.domain.entities.role import Role
from api.domain.entities.tenant import validate_subdomain
from api.domain.entities.user import User
from api.domain.enum.permission import Permission
from api.domain.enum.role import RoleType
from api.domain.interfaces.email_service import IEmailService
from api.infrastructure.security.jwt_token_service import JwtTokenService
from api.interfaces.email_templates.password_reset_email_template_html import password_reset_email_template_html
from api.interfaces.email_templates.notify_password_changes_template_html import notify_password_change_template_html
from api.interfaces.email_templates.activation_template_html import activation_template_html
from api.interfaces.email_templates.email_changes_confirmation_template_html import email_changes_confirmation_template_html
from api.interfaces.email_templates.notify_email_changes_template_html import notify_email_change_template_html
from api.usecases.audit_logs_service import AuditLogsService
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
            email_service: IEmailService,
            audit_log_service: AuditLogsService
        ):
        self.user_service: UserService = user_service
        self.tenant_service: TenantService = tenant_service
        self.role_service: RoleService = role_service
        self.jwt_token_service: JwtTokenService = jwt_token_service
        self.email_service: IEmailService = email_service
        self.audit_log_service: AuditLogsService = audit_log_service
        logger.info("Initialized.")
        print(self.email_service, "email service in auth service")

    async def _get_token_set(self, user: User) -> TokenSetDto:
        """
            Helper method to generate a TokenSetDto for the given user. Dont use this method outside this class.
        """
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

        res = await self.jwt_token_service.generate_tokens(payload)
        await self.audit_log_service.create_audit_log(audit_log=AuditLogDto(
            entity="User",
            action="login",
            user_id=str(user.id),
            tenant_id=str(user.tenant_id) if user.tenant_id else None,
            changes={"Info": f"User received tokens and logged in."}
        ))
        
        # Host audit log for tenant admin login
        if user.tenant_id and Permission.FULL_ACCESS in (role.permissions if role.permissions else []):
            logger.info(f"Tenant ID: {user.tenant_id} logged in. Updating an audit log in the host.")
            await self.audit_log_service.create_audit_log(audit_log=AuditLogDto(
                entity="User",
                action="login",
                user_id=str(user.id),
                tenant_id=None,
                changes={"Info": f"Tenant admin user logged in."}
            ))
        return res


    async def login_with_magic_link(self, user_id: str) -> TokenSetDto:
        try:
  
            user = await self.user_service.get_user_by_id(user_id=user_id)
            await self.audit_log_service.create_audit_log(audit_log=AuditLogDto(
                entity="User",
                action="login",
                user_id=user_id,
                changes={"Info": f"User attempted to log in with magic link."},
                tenant_id=str(user.tenant_id) if user.tenant_id else None
            ))
            return await self._get_token_set(user)
        except UserNotFoundException or Exception:
            logger.error(f"Login attempt failed for user_id: {user_id}")
            await self.audit_log_service.create_audit_log(audit_log=AuditLogDto(
                entity="User",
                action="error",
                user_id=str(user.id),
                tenant_id=str(user.tenant_id) if user.tenant_id else None,
                changes={"Info": f"User with an email: {user.email} failed to log in."}
            ))
            raise UnauthorizedException("Authentication failed. Please check your credentials.")


    async def login_with_passkey(self, email: str) -> TokenSetDto:
        try:
            user = await self.user_service.find_by_email(email=email)
            await self.audit_log_service.create_audit_log(audit_log=AuditLogDto(
                entity="User",
                action="login",
                user_id=str(user.id),
                tenant_id=str(user.tenant_id) if user.tenant_id else None,
                changes={"Info": f"User attempted to log in with passkey."}
            ))
            return await self._get_token_set(user)
        except UserNotFoundException or Exception:
            logger.error(f"Login attempt failed for email: {email}")
            await self.audit_log_service.create_audit_log(audit_log=AuditLogDto(
                entity="User",
                action="error",
                user_id="unknown",
                changes={"Info": f"User with an email: {email} failed to log in with passkey."}
            ))
            raise UnauthorizedException("Authentication failed. Please check your credentials.")


    async def login(self, req: LoginRequestDto) -> TokenSetDto:
        user = await self.user_service.find_by_email(email=req.email)
        if verify_password(req.password, user.password) is False:
            raise UnauthorizedException("Authentication failed. Please check your credentials.")

        return await self._get_token_set(user)
    
    async def login_with_sso(self, provider_name: str, user_info: OpenID) -> TokenSetDto:
        email = user_info.email
        display_name = user_info.display_name
        first_name = user_info.first_name
        last_name = user_info.last_name
        provider_id = provider_name
        if email is None:
            raise InvalidOperationException("SSO provider did not return an email address.")
        try:
            user = await self.user_service.find_by_email(email=email)
            return await self._get_token_set(user)
        except UserNotFoundException:
            logger.error(f"User not found for email: {email}")
            role: Role = await self.role_service.find_by_name(name=RoleType.GUEST)  # Ensure default role exists
            await self.user_service.create_user(user_data=CreateUserDto(
                email=email,
                first_name=first_name or display_name or "N/A",
                last_name=last_name or display_name or "N/A",
                password=f"signed_up_via_sso_{provider_id}",
                sso_provider_id=provider_id,
                gender="prefer_not_to_say",
                role_id=role.id if role else None
            ))
        
        user = await self.user_service.find_by_email(email=email)
        return await self._get_token_set(user)


    async def register(self, new_user: CreateUserDto, cb: Callable) -> None:
        """
            Register a new user. In multi-tenant mode, if the subdomain is unique, a new tenant will be created.
            The callback function `cb` will be called with the newly created tenant ID after tenant creation.
            In single-tenant mode, the user will be created without a tenant.
            Raises InvalidOperationException if the subdomain is already taken in multi-tenant mode.
            The user will be created with the provided details.
        """

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
                    await self.audit_log_service.create_audit_log(audit_log=AuditLogDto(
                        entity="Tenant",
                        action="error",
                        user_id="unknown",
                        changes={"Info": f"Tenant with subdomain: {new_user.sub_domain} is already taken."},
                        tenant_id=str(tenant.id)
                    ))
                    raise InvalidOperationException(f"Subdomain '{new_user.sub_domain}' is already taken.")
            except InvalidOperationException as ioe:
                logger.warning(f"Subdomain validation failed for '{new_user.sub_domain}': {ioe}")
                # If it is coming here.. that means the request is valid and made by a legit tenant.. because the tenant middleware has already validated it.
                await self.user_service.create_user(user_data=new_user)
        
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

    async def logout(self, user_id: str, tenant_id: str | None) -> None:
        await self.audit_log_service.create_audit_log(audit_log=AuditLogDto(
            entity="User",
            action="logout",
            user_id=user_id,
            tenant_id=tenant_id,
            changes={"Info": f"User logged out and refresh tokens invalidated."}
        ))
        logger.info(f"User {user_id} logged out successfully and refresh tokens invalidated.")
    
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



    async def initate_password_reset(self, email: EmailStr, domain: str) -> None:
        """
            Initiate the password reset process by sending a password reset email to the user.
            Raises InvalidOperationException if the user with the provided email does not exist.
            Sends a password reset email with a link to reset the password.
        """
        reset_data = await self.user_service.request_password_reset(email)
        data = ActivationTokenPayloadDto(
            user_id=str(reset_data.user_id),
            email=email,
            type="password_reset_confirmation",
            jwt_secret=reset_data.token_secret,
            tenant_id=str(reset_data.tenant_id)
        )
        token = await self.jwt_token_service.encode_activation_token(data)
        link = get_email_sharing_link(token=token, user_id=str(reset_data.user_id), domain=domain, type=data.type, tenant_id=str(reset_data.tenant_id))
        html = password_reset_email_template_html(user_first_name=reset_data.first_name, password_reset_link=link)
        await self.email_service.send_email(
            to=email,
            subject="Password Reset Request",
            body=html,
            type=MessageType.html
        )
        logger.info(f"Password reset initiated for user {reset_data.user_id} ({email})")
            

    async def change_password(self, new_password: str, token: str, user_id: str) -> None:
        """
            Change the user's password using the provided password reset token.
            Raises InvalidOperationException if the token is invalid or expired.
            On success, updates the user's password and clears the password reset data.
        """
        reset_data = await self.user_service.retrieve_password_reset_data_by_user_id(user_id=user_id)
        if reset_data is None:
            raise InvalidOperationException("Invalid or expired password reset token.")
        payload = await self.jwt_token_service.verify_password_reset_token(token=token, jwt_secret=reset_data.token_secret)
        if payload.user_id != user_id:
            raise InvalidOperationException("Invalid password reset token.")
        await self.user_service.update_user_password(user_id=user_id, new_password=new_password)
        await reset_data.delete()
        logger.info(f"Password reset successful for user {user_id}. Cleared reset data.")
        html = notify_password_change_template_html(user_first_name=reset_data.first_name)
        await self.email_service.send_email(
            to=payload.email,
            subject="Your Password Has Been Changed",
            body=html,
            type=MessageType.html
        )
    

    async def send_activation_email(self, payload: UserResendActivationEmailRequestDto, domain: str) -> None:
        """
            Resend the activation email to the user.
            Raises InvalidOperationException if the user is already active.
            Sends an activation email with a link to activate the account.
        """
        user = await self.user_service.find_by_email(email=payload.email)
        if user.is_active:
            raise InvalidOperationException("User is already active.")
        activation_token = await self.jwt_token_service.encode_activation_token(payload=ActivationTokenPayloadDto(
            user_id=str(payload.id),
            email=payload.email,
            type="activation",
            tenant_id=payload.tenant_id
        ))
        link = get_email_sharing_link(token=activation_token, user_id=payload.id, domain=domain, type="activation", tenant_id=payload.tenant_id)
        html = activation_template_html(user_first_name=payload.first_name, activation_link=link)
        await self.email_service.send_email(
            to=payload.email,
            subject="Account Activation",
            body=html,
            type=MessageType.html
        )
        logger.info(f"Activation email sent to {payload.email}")


    async def activate_account(self, req: UserActivationRequestDto) -> None:
        """
            Activate a user account using the provided activation token.
            Raises InvalidOperationException if the user is already active or if the token is invalid.
        """
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
        

    async def change_email_request(self, current_email: EmailStr, new_email: EmailStr, domain: str) -> None:
        """
            Initiate the email change process by sending a confirmation email to the new email address.
            Raises InvalidOperationException if the new email is the same as the current email or if the new email is already in use.
            Sends a confirmation email to the new email address with a link to confirm the email change.
            The actual email change is completed in the `change_email_confirmation` method.
        """
        if current_email == new_email:
            raise InvalidOperationException("The new email address must be different from the current email address.")
        
        does_exist = await self.user_service.check_email_exists(email=new_email)
        if does_exist is True:
            raise InvalidOperationException(f"The email '{new_email}' is already in use by another account.")
        
        user = await self.user_service.find_by_email(email=current_email)
        activation_token = await self.jwt_token_service.encode_activation_token(payload=ActivationTokenPayloadDto(
            user_id=str(user.id),
            email=new_email,
            type="change_email_confirmation",
            tenant_id=user.tenant_id
        ))
        link = get_email_sharing_link(token=activation_token, user_id=str(user.id), domain=domain, type="change_email_confirmation", tenant_id=str(user.tenant_id))
        html = email_changes_confirmation_template_html(user_first_name=user.first_name, email_change_link=link)
        await self.email_service.send_email(
            to=user.email,
            subject="Confirm Your Email Change",
            body=html,
            type=MessageType.html
        )

    async def change_email_confirmation(self, token: str) -> None:
        """
            Confirm and complete the email change process.
            Raises InvalidOperationException if the new email is already in use.
            Updates the user's email to the new email address after confirmation.
            Sends a notification email to the user about the email change.
        """
        payload = await self.jwt_token_service.verify_change_email_token(token=token)
        user = await self.user_service.get_user_by_id(user_id=payload.user_id)
        does_exist = await self.user_service.check_email_exists(email=payload.email)
        if does_exist is True:
            raise InvalidOperationException(f"The email '{payload.email}' is already in use by another account. Cannot change email.")
        
        user.email = payload.email
        logger.info(f"User {user.id} changed email to {payload.email}.")
        await user.save()
        html = notify_email_change_template_html(user_first_name=user.first_name)
        await self.email_service.send_email(
            to=user.email,
            subject="Your Email Has Been Changed Successfully",
            body=html,
            type=MessageType.html
        )


    async def get_user_service(self) -> UserService:
        return self.user_service