from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from passlib.hash import pbkdf2_sha256
from api.core.config import settings

JWT_SECRET = settings.jwt_secret

REFRESH_TOKEN_SECRET = settings.refresh_token_secret

ALGORITHM = settings.algorithm

REFRESH_ALGORITHM = settings.refresh_algorithm

ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/account/login", auto_error=False)
tenant_header = APIKeyHeader(name="x-tenant-id", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pbkdf2_sha256.verify(plain_password, hashed_password)


def hash_it(password: str) -> str:
    return pbkdf2_sha256.hash(password)

