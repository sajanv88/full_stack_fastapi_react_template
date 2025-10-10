from datetime import timedelta
from typing import Literal

import jwt
from api.common.dtos.token_dto import AccessTokenDto, ActivationTokenPayloadDto, RefreshTokenDto, RefreshTokenDto, RefreshTokenPayloadDto, TokenPayloadDto, TokenSetDto, VerifyEmailTokenPayloadDto
from api.common.utils import get_logger, get_utc_now
from api.common.security import ACCESS_TOKEN_EXPIRE_MINUTES, ACTIVATION_TOKEN_EXPIRE_HOURS, ALGORITHM, JWT_SECRET, REFRESH_ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS, REFRESH_TOKEN_SECRET
from api.common.exceptions import InvalidOperationException

logger  = get_logger(__name__)
class JwtTokenService:
    def __init__(self):
        logger.info("Initialized.")

    async def get_access_token(self, payload: TokenPayloadDto, expires_delta: timedelta | None = None) -> AccessTokenDto:
        to_encode = payload.model_dump()
        if expires_delta:
            expire = get_utc_now() + expires_delta
        else:
            expire = get_utc_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
        return AccessTokenDto(access_token=encoded_jwt, token_type="bearer", expires_in=expire)

    async def get_refresh_token(self, payload: TokenPayloadDto, expires_delta: timedelta | None = None) -> RefreshTokenDto:
        to_encode = {"sub": str(payload.sub), "tenant_id": str(payload.tenant_id) if payload.tenant_id else None, "type": "refresh"}
        if expires_delta:
            expire = get_utc_now() + expires_delta
        else:
            expire = get_utc_now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, REFRESH_TOKEN_SECRET, algorithm=REFRESH_ALGORITHM)
        return RefreshTokenDto(refresh_token=encoded_jwt, refresh_token_expires_in=expire)
    
    async def generate_tokens(self, payload: TokenPayloadDto) -> TokenSetDto:
        """
            Generate access and refresh tokens.
        """
        access_token = await self.get_access_token(payload)
        refresh_token = await self.get_refresh_token(payload)
        return TokenSetDto(
            access_token=access_token.access_token,
            token_type=access_token.token_type,
            expires_in=int((access_token.expires_in - get_utc_now()).total_seconds()),
            refresh_token=refresh_token.refresh_token,
            refresh_token_expires_in=int((refresh_token.refresh_token_expires_in - get_utc_now()).total_seconds())
        )
    
    async def decode_token(
            self,
            token: str, type: Literal["access_token", "refresh_token"] = "access_token") -> TokenPayloadDto | RefreshTokenPayloadDto | None :
        try:
            if type == "access_token":
                payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
                return TokenPayloadDto(**payload)
            elif type == "refresh_token":
                payload = jwt.decode(token, REFRESH_TOKEN_SECRET, algorithms=[REFRESH_ALGORITHM])
                logger.debug(f"Decoded refresh token payload: {payload}")
                return RefreshTokenPayloadDto(sub=payload.get("sub"), tenant_id=payload.get("tenant_id", None), type=payload.get("type"))
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired.")
            return None
        except jwt.InvalidTokenError:
            logger.error("Invalid token.")
            return None

    async def verify_activation_token(self, token: str) -> VerifyEmailTokenPayloadDto:
        """
        Verify and decode the activation token.
        Returns user_id and email if valid, raises exception if invalid.
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
            if payload.get("type") != "activation":
                raise jwt.InvalidTokenError("Invalid token type")
            
            return VerifyEmailTokenPayloadDto(
                user_id=payload.get("user_id"),
                email=payload.get("email")
            )
        except jwt.ExpiredSignatureError:
            logger.error("Activation token has expired")
            raise InvalidOperationException("Activation token has expired")
        except jwt.InvalidTokenError:
            logger.error("Invalid activation token")
            raise InvalidOperationException("Invalid activation token")


    async def verify_password_reset_token(self, token: str, jwt_secret: str) -> VerifyEmailTokenPayloadDto:
        """
            Verify and decode the password reset token.
            Returns user_id and email if valid, raises exception if invalid.
        """
        try:
            payload = jwt.decode(token, jwt_secret, algorithms=[ALGORITHM])
            logger.debug(f"Decoded password reset token payload: {payload}")
            if payload.get("type") != "password_reset_confirmation":
                logger.debug(f"Invalid token type: {payload.get('type')}")
                raise InvalidOperationException("Invalid token type")
            return VerifyEmailTokenPayloadDto(
                user_id=payload.get("user_id"),
                email=payload.get("email")
            )
        except jwt.ExpiredSignatureError:
            logger.error("Password reset token has expired")
            raise InvalidOperationException("Password reset token has expired")
        except jwt.InvalidTokenError:
            logger.error("Invalid password reset token")
            raise InvalidOperationException("Invalid password reset token")
    
    async def verify_change_email_token(self, token: str) -> VerifyEmailTokenPayloadDto:
        """
            Verify and decode the change email token.
            Returns user_id and email if valid, raises exception if invalid.
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
            logger.debug(f"Decoded change email token payload: {payload}")
            if payload.get("type") != "change_email_confirmation":
                logger.debug(f"Invalid token type: {payload.get('type')}")
                raise jwt.InvalidTokenError("Invalid token type")
            return VerifyEmailTokenPayloadDto(
                user_id=payload.get("user_id"),
                email=payload.get("email")
            )
        except jwt.ExpiredSignatureError:
            logger.error("Change email token has expired")
            raise InvalidOperationException("Change email token has expired")
        except jwt.InvalidTokenError:
            logger.error("Invalid change email token")
            raise InvalidOperationException("Invalid change email token")


    async def encode_activation_token(self, payload: ActivationTokenPayloadDto) -> str:
        """
            Generate a JWT token for account activation.
        """

        expire = get_utc_now() + timedelta(hours=ACTIVATION_TOKEN_EXPIRE_HOURS)

        data = {
            "user_id": payload.user_id,
            "email": payload.email,
            "type": payload.type,
            "exp": expire,
            "iat": get_utc_now(),
            "tenant_id": payload.tenant_id
        }

        return jwt.encode(data, payload.jwt_secret or JWT_SECRET, algorithm=ALGORITHM)


