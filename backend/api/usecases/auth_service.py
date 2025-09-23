from fastapi.params import Depends
from api.common.dtos.token_dto import TokenPayloadDto, TokenSetDto
from api.common.exceptions import UnauthorizedException
from api.common.security import verify_password
from api.common.utils import get_logger
from api.domain.dtos.login_dto import LoginRequestDto
from api.domain.dtos.role_dto import RoleDto
from api.infrastructure.security.jwt_token_service import JwtTokenService
from api.usecases.role_service import RoleService
from api.usecases.tenant_service import TenantService
from api.usecases.user_service import UserService

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