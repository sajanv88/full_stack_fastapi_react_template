import logging
import os
from typing_extensions import Annotated
import jwt
from datetime import datetime, timedelta, timezone
from typing import  Optional, Union
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from app.models.role import Role
from app.core.utils import oauth2_scheme_no_error

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret_key")
REFRESH_TOKEN_SECRET = os.getenv("REFRESH_TOKEN_SECRET", "your_refresh_jwt_secret_key")
ALGORITHM = "HS256"
REFRESH_ALORITHM = "HS512"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7



class TokenSet(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    refresh_token_expires_in: int

class TokenData(BaseModel):
    email: str
    sub: str
    role: Optional[Role]
    is_active: Optional[bool] = False
    activated_at: Optional[str] = None
    tenant_id: Optional[str] = None


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return {"access_token": encoded_jwt, "token_type": "bearer", "expires_in": expire}


def create_refresh_token(user_id: str, expires_delta: timedelta | None = None):
    to_encode = {"sub": user_id, "exp": expires_delta}.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_TOKEN_SECRET, algorithm=REFRESH_ALORITHM)
    return {"refresh_token": encoded_jwt,  "refresh_token_expires_in": expire}


def generate_token_set(data: dict, access_token_expires: timedelta | None = None, refresh_token_expires: timedelta | None = None) -> TokenSet:

    access_token_info = create_access_token(data, access_token_expires)
    refresh_token_info = create_refresh_token(data["sub"], refresh_token_expires)
    
    return TokenSet(
        access_token=access_token_info["access_token"],
        token_type=access_token_info["token_type"],
        expires_in=int((access_token_info["expires_in"] - datetime.now(timezone.utc)).total_seconds()),
        refresh_token=refresh_token_info["refresh_token"],
        refresh_token_expires_in=int((refresh_token_info["refresh_token_expires_in"] - datetime.now(timezone.utc)).total_seconds())
    )

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
            )

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, REFRESH_TOKEN_SECRET, algorithms=[REFRESH_ALORITHM])
        return payload
    except InvalidTokenError:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
            )
    

def get_token_decoded_payload(token: Annotated[Union[str, None], Depends(oauth2_scheme_no_error)]) -> Union[TokenData , None]:
    if token is None:
        return None
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        logger.debug(f"Decoded token payload: {payload}")
        return TokenData(**payload).model_dump()
    except InvalidTokenError:
        logger.warning("Invalid token provided")
        return None
    