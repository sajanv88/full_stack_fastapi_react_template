from fastapi import Depends, APIRouter, status, HTTPException, Response
from jwt import InvalidTokenError
from pydantic import BaseModel
from app.core.db import user_collection
from app.models.user import NewUser, User
from bson import ObjectId
from passlib.context import CryptContext
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.token import TokenSet, verify_refresh_token, verify_token, TokenData, generate_token_set
from app.schemas.user_schema import seralize_user_schema


router = APIRouter(prefix="/auth")
router.tags = ["Auth"]

class LoginRequest(BaseModel):
     email: str
     password: str

class RefreshRequest(BaseModel):
    refresh_token: str



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", refreshUrl="api/auth/refresh")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(email=payload["email"], sub=payload["sub"])
    except InvalidTokenError:
        raise credentials_exception
    user = await user_collection.find_one({"_id": ObjectId(token_data.sub)})
    if user is None:
        raise credentials_exception
    return user



 
@router.post("/login", response_model=TokenSet)
async def login(login_request: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await user_collection.find_one({"email": login_request.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    if not verify_password(login_request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token_data = {"sub": str(user["_id"]), "email": user["email"]}
    return generate_token_set(token_data)


@router.post("/register", response_class=Response)
async def register(new_user: NewUser):
    existing_user = await user_collection.find_one({"email": new_user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(new_user.password)
    user_dict = new_user.model_dump().copy()
    user_dict["password"] = hashed_password
    
    result = await user_collection.insert_one(user_dict)
    if result.inserted_id:
        return Response(status_code=status.HTTP_201_CREATED)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user"
        )
    

@router.get("/me", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return seralize_user_schema(current_user)


@router.post("/refresh", response_model=TokenSet)
async def refresh_token(token: RefreshRequest):
    try:
        refresh_token = token.refresh_token
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        user = await user_collection.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        token_data = {"sub": str(user["_id"]), "email": user["email"]}
        return generate_token_set(token_data)
    except InvalidTokenError:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
            )
