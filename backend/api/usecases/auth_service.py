from api.common.dtos.token_dto import TokenPayloadDto, TokenSetDto
from api.common.exceptions import InvalidOperationException, UnauthorizedException
from api.common.security import verify_password
from api.common.utils import get_logger, is_tenancy_enabled
from api.core.exceptions import TenantNotFoundException
from api.domain.dtos.login_dto import LoginRequestDto
from api.domain.dtos.role_dto import RoleDto
from api.domain.dtos.tenant_dto import CreateTenantDto
from api.domain.dtos.user_dto import CreateUserDto
from api.domain.entities.tenant import validate_subdomain
from api.infrastructure.security.jwt_token_service import JwtTokenService
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
            jwt_token_service: JwtTokenService
        ):
        self.user_service: UserService = user_service
        self.tenant_service: TenantService = tenant_service
        self.role_service: RoleService = role_service
        self.jwt_token_service: JwtTokenService = jwt_token_service
        logger.info("Initialized.")

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

    


            

            

            