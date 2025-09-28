from typing import Annotated
from api.common.security import oauth2_scheme
from api.core.exceptions import InvalidOperationException
from api.common.exceptions import UnauthorizedException
from api.common.utils import get_logger
from api.domain.dtos.user_dto import UserDto
from api.infrastructure.security.jwt_token_service import JwtTokenService
from api.usecases.user_service import UserService
from api.core.container import get_user_service, get_jwt_token_service  
from fastapi import Depends


logger = get_logger(__name__)

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        user_service: UserService = Depends(get_user_service),
        token_service: JwtTokenService = Depends(get_jwt_token_service)
    ) -> UserDto:
    payload = await token_service.decode_token(token, type="access_token")
    if payload is None:
        logger.error("Payload is None after decoding token.")
        raise UnauthorizedException("JWT token is invalid or has expired.")
    user = await user_service.get_user_by_id(user_id=str(payload.sub))
    if user is None:
        logger.error(f"User not found for ID: {payload.sub}")
        raise InvalidOperationException("User associated with the token not found.")

    user_doc = await user.to_serializable_dict()
    return UserDto(**user_doc)


CurrentUser = Annotated[UserDto, Depends(get_current_user)]